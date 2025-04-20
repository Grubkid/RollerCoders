# App/models/user_recipe.py

from App.database import db

class UserRecipe(db.Model):
    __tablename__ = 'user_recipe'

    id        = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

    # enforce one‐per‐user/per‐recipe
    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id', name='uix_user_recipe'),
    )

    # relationships for easy joins
    user      = db.relationship('User', back_populates='recipes')
    recipe    = db.relationship('Recipe', back_populates='users')
