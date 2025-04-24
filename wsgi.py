import click, pytest, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import upgrade  # Import upgrade for database migrations

from App.views.auth import auth_views
from App.views.ingredient import ingredient_views
from App.views.recipe import recipe_views
from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import (
    create_user, 
    get_all_users_json, 
    get_all_users, 
    initialize
)

# Create and configure app
app = create_app()

# Automatically initialize the database in production
with app.app_context():
    try:
        # Apply migrations to ensure the database is up-to-date
        upgrade()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing the database: {e}")

if __name__ == "__main__":
    app.run()

