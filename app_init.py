import os
import logging
from flask import Flask
from routes import register_routes
from database import db, run_migrations
from dotenv import load_dotenv
from markupsafe import Markup
import markdown2

def create_initialized_flask_app():
    load_dotenv()  # Load environment variables from .env file
    app = Flask(__name__, static_folder='static')

    # Initialize database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
    db.init_app(app)

    # Run migrations
    run_migrations(app)

    # Register markdown filter
    app.jinja_env.filters['markdown'] = lambda text: Markup(markdown2.markdown(text))

    register_routes(app)

    return app