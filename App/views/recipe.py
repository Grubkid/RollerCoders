from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from App.controllers.recipe import search_recipes_for_user, lookup_full_recipe, save_recipe_for_user, get_saved_recipes, get_all_categories, get_all_areas
from App.controllers.ingredient import get_user_ingredients
from App.models.recipe import Recipe
from App.cache import get_cached_categories, get_cached_areas

recipe_views = Blueprint('recipe_views', __name__, template_folder='../templates')


@recipe_views.route('/recipes/search', methods=['GET', 'POST'])
@jwt_required()
def recipe_search():
    user_id = get_jwt_identity()
    recipes = search_recipes_for_user(user_id)

    # get filter options
    # categories = get_all_categories()
    # areas = get_all_areas()

    categories = get_cached_categories()
    areas = get_cached_areas()

    # get selected filters from form (POST) or query (GET)
    selected_category = request.form.get('category') or request.args.get('category')
    selected_area = request.form.get('area') or request.args.get('area')

    # filter recipes locally
    if selected_category:
        recipes = [r for r in recipes if r.get('strCategory') == selected_category]
    if selected_area:
        recipes = [r for r in recipes if r.get('strArea') == selected_area]

    return render_template('recipes.html',
        recipes=recipes,
        categories=categories,
        areas=areas,
        selected_category=selected_category,
        selected_area=selected_area
    )

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

@recipe_views.route('/recipes/<id>/save', methods=['POST'])
@jwt_required()
def save_recipe(id):
    user_id = get_jwt_identity()
    recipe = lookup_full_recipe(id)
    if save_recipe_for_user(user_id, recipe):
        flash('Recipe saved to your collection!', 'success')
    else:
        flash('Recipe was already saved.', 'info')
    return redirect(url_for('recipe_views.recipe_detail', id=id))

@recipe_views.route('/recipes/my', methods=['GET'])
@jwt_required()
def my_recipes():
    user_id = get_jwt_identity()
    recipes = get_saved_recipes(user_id)
    return render_template('my_recipes.html', recipes=recipes)

from App.controllers.recipe import remove_saved_recipe

@recipe_views.route('/recipes/<id>/remove', methods=['POST'])
@jwt_required()
def remove_recipe(id):
    user_id = get_jwt_identity()
    # Look up recipe by API ID to get local DB ID
    local = Recipe.query.filter_by(api_recipe_id=id).first()
    if local and remove_saved_recipe(user_id, local.id):
        flash("Recipe removed from your collection.", "success")
    else:
        flash("Recipe not found in your saved list.", "error")
    return redirect(url_for('recipe_views.my_recipes'))