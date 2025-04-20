from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.controllers.recipe import search_recipes_for_user

recipe_views = Blueprint('recipe_views', __name__, template_folder='../templates')

@recipe_views.route('/recipes/search', methods=['GET'])
@jwt_required()
def recipe_search():
    """Show recipes matching the user's inventory ingredients."""
    user_id = get_jwt_identity()
    recipes = search_recipes_for_user(user_id)
    return render_template('recipes.html', recipes=recipes)

@recipe_views.route('/recipes/<id>', methods=['GET'])
@jwt_required()
def recipe_detail(id):
    recipe = lookup_full_recipe(id)
    # extract list of {ingredient, measure}
    ingredients = []
    for i in range(1, 21):
        name = recipe.get(f'strIngredient{i}')
        meas = recipe.get(f'strMeasure{i}')
        if name: ingredients.append({'name': name, 'measure': meas})
    # compute missing
    user_names = {u['name'].lower() for u in get_user_ingredients(get_jwt_identity())}
    for ing in ingredients:
        ing['missing'] = ing['name'].lower() not in user_names
    return render_template('recipe_detail.html', recipe=recipe, ingredients=ingredients)
