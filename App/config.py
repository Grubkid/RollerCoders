import os
from datetime import timedelta  # Import timedelta

def load_config(app, overrides):
    # Load environment-specific configuration
    if os.path.exists(os.path.join('./App', 'custom_config.py')):
        app.config.from_object('App.custom_config')
    else:
        app.config.from_object('App.default_config')

    # Load additional secrets and API keys
    app.config['ENV'] = os.environ.get('ENV', 'DEVELOPMENT')
    if app.config['ENV'] == "DEVELOPMENT":
        from .default_config import JWT_ACCESS_TOKEN_EXPIRES, SQLALCHEMY_DATABASE_URI, SECRET_KEY
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        app.config['SECRET_KEY'] = SECRET_KEY
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = JWT_ACCESS_TOKEN_EXPIRES
    else:
        # For production, ensure these values are set via environment variables
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(
            days=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 7))  # Convert to timedelta
        )

    # Additional Flask configurations
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOADED_PHOTOS_DEST'] = "App/uploads"
    app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
    app.config["JWT_TOKEN_LOCATION"] = ["cookies", "headers"]
    app.config["JWT_COOKIE_SECURE"] = True
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False
    app.config['FLASK_ADMIN_SWATCH'] = 'darkly'

    # Apply overrides if provided
    for key in overrides:
        app.config[key] = overrides[key]