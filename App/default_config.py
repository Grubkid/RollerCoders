from datetime import timedelta  # Add this import

SQLALCHEMY_DATABASE_URI = "sqlite:///temp-database.db"
SECRET_KEY = "secret key"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)  # Set expiration to 7 days
ENV = "DEVELOPMENT"