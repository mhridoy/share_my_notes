from flask import render_template, abort, make_response
from flask import current_app as app
import os
from github import Github

def register_routes(app):
    @app.route("/")
    def home_route():
        return render_template("home.html")

    @app.route("/topic/<topic>")
    def topic_route(topic):
        topics = {
            'searching-algorithms': 'Searching Algorithms',
            'turing-test': 'Turing Test',
            '8-puzzle-problem': '8-Puzzle Problem',
            'a-star-search': 'A* Search',
            'peas-in-ai': 'PEAS in AI',
            'hill-climbing-algorithm': 'Hill Climbing Algorithm'
        }
        if topic not in topics:
            abort(404)
        content = get_topic_content(topic)
        return render_template("topic.html", topic=topics[topic], content=content)

    def get_topic_content(topic):
        from abilities import llm
        prompt = f"""Provide a detailed explanation of the AI topic: {topic}. Include its importance, key concepts, algorithms if applicable, and real-world applications. The explanation should be comprehensive and suitable for an educational platform. Structure the content as follows:
        1. Introduction
        2. Key Concepts
        3. Algorithms (if applicable)
        4. Real-world Applications
        5. Conclusion
        Use markdown formatting for headers, lists, and emphasis. Make sure to use ## for main sections and ### for subsections."""
        response_schema = {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Detailed explanation of the AI topic in markdown format"
                }
            },
            "required": ["content"]
        }
        response = llm(prompt=prompt, response_schema=response_schema, image_url=None, model="gpt-4o", temperature=0.7)
        return response['content']

    @app.route("/download/<topic>")
    def download_topic(topic):
        from fpdf import FPDF
        content = get_topic_content(topic)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, content)
        pdf_output = pdf.output(dest='S').encode('latin-1')
        response = make_response(pdf_output)
        response.headers["Content-Disposition"] = f"attachment; filename={topic.replace(' ', '_')}.pdf"
        response.headers["Content-Type"] = "application/pdf"
        return response

    def create_github_repo():
        g = Github(os.environ['GITHUB_TOKEN'])
        user = g.get_user()
        repo = user.create_repo("share_my_notes")
        return repo

    def commit_and_push(repo, file_path, content, commit_message):
        repo.create_file(file_path, commit_message, content)

    # Create the repository
    repo = create_github_repo()

    # Commit and push the main files
    commit_and_push(repo, "main.py", open("main.py", "r").read(), "Add main.py")
    commit_and_push(repo, "routes.py", open("routes.py", "r").read(), "Add routes.py")
    commit_and_push(repo, "app_init.py", open("app_init.py", "r").read(), "Add app_init.py")
    commit_and_push(repo, "database.py", open("database.py", "r").read(), "Add database.py")
    commit_and_push(repo, "requirements.txt", open("requirements.txt", "r").read(), "Add requirements.txt")

    # Commit and push the template files
    for template_file in os.listdir("templates"):
        file_path = os.path.join("templates", template_file)
        commit_and_push(repo, file_path, open(file_path, "r").read(), f"Add {file_path}")

    # Commit and push the static files
    for static_file in os.listdir("static"):
        file_path = os.path.join("static", static_file)
        commit_and_push(repo, file_path, open(file_path, "r").read(), f"Add {file_path}")