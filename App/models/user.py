from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from App.models.ingredient import Ingredient

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    ingredients = db.relationship('Ingredient', backref='user', lazy=True)
    recipes = db.relationship('UserRecipe', back_populates='user', lazy=True)


    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

