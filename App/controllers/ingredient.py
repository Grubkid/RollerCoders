import requests 
from App.models import Ingredient
from flask import Blueprint, render_template, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.database import db

ingredient_views = Blueprint('ingredient_views', __name__, template_folder='../templates')


def fetch_ingredients_from_api():
    """Fetch ingredients from the external API."""
    try:
        res = requests.get('https://www.themealdb.com/api/json/v1/1/list.php?i=list')
        if res.status_code == 200:
            return res.json().get('meals', [])
        return []
    except Exception as e:
        print(f"Error fetching ingredients: {e}")
        return []
    

@ingredient_views.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    ingredients = fetch_ingredients_from_api()
    return render_template('dashboard.html', api_ingredients=ingredients, user_id=user_id)

def search_ingredients(query):
    """Search for ingredients from the API based on a query."""
    ingredients = fetch_ingredients_from_api()
    return [ing for ing in ingredients if query.lower() in ing['strIngredient'].lower()]

def add_ingredient_to_user(user_id, ingredient_id, name, quantity):
    """Add an ingredient to the user's inventory."""
    existing = Ingredient.query.filter_by(user_id=user_id, ingredient_id=ingredient_id).first()
    if existing:
        existing.quantity += quantity
    else:
        new_ingredient = Ingredient(
            ingredient_id=ingredient_id,
            name=name,
            quantity=quantity,
            user_id=user_id
        )
        db.session.add(new_ingredient)
    db.session.commit()

def remove_ingredient_from_user(user_id, ingredient_id):
    """Remove an ingredient from the user's inventory."""
    ingredient = Ingredient.query.filter_by(user_id=user_id, ingredient_id=ingredient_id).first()
    if ingredient:
        db.session.delete(ingredient)
        db.session.commit()
        return True
    return False

def update_ingredient_quantity(user_id, ingredient_id, quantity):
    """Update the quantity of an ingredient in the user's inventory."""
    ingredient = Ingredient.query.filter_by(user_id=user_id, ingredient_id=ingredient_id).first()
    if ingredient:
        ingredient.quantity = quantity
        db.session.commit()
        return True
    return False

def get_user_ingredients(user_id):
    """Retrieve all ingredients in the user's inventory."""
    ingredients = Ingredient.query.filter_by(user_id=user_id).all()
    print(f"Retrieved ingredients for user_id={user_id}: {ingredients}")
    return [ing.to_dict() for ing in ingredients]
