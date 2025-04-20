# App/models/recipe.py

from App.database import db

class Recipe(db.Model):
    __tablename__ = 'recipe'

    id             = db.Column(db.Integer, primary_key=True)
    api_recipe_id  = db.Column(db.String(50), unique=True, nullable=False)   # maps to idMeal
    name           = db.Column(db.String(200), nullable=False)               # strMeal
    category       = db.Column(db.String(100))                               # strCategory
    area           = db.Column(db.String(100))                               # strArea
    instructions   = db.Column(db.Text)                                       # strInstructions
    thumbnail      = db.Column(db.String(500))                               # strMealThumb
    tags           = db.Column(db.JSON)                                      # strTags → list of tags
    youtube_url    = db.Column(db.String(500))                               # strYoutube
    source_url     = db.Column(db.String(500))                               # strSource
    date_modified  = db.Column(db.String(50))                                # dateModified

    # ingredients: list of {"ingredient": str, "measure": str}
    ingredients    = db.Column(db.JSON, nullable=False)

    # relationship back to users who saved this recipe
    users          = db.relationship('UserRecipe', back_populates='recipe', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'api_recipe_id': self.api_recipe_id,
            'name': self.name,
            'category': self.category,
            'area': self.area,
            'instructions': self.instructions,
            'thumbnail': self.thumbnail,
            'tags': self.tags or [],
            'youtube_url': self.youtube_url,
            'source_url': self.source_url,
            'date_modified': self.date_modified,
            'ingredients': self.ingredients
        }
