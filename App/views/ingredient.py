from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user, unset_jwt_cookies
from flask import jsonify
import requests
import os
import json

# Compute the path to your JSON file
JSON_PATH = os.path.join(
    os.path.dirname(__file__),   # App/views
    'ingredient_list.json'
)

# Load once at import time
with open(JSON_PATH, 'r', encoding='utf-8') as f:
    LOCAL_INGREDIENTS = json.load(f).get('meals', [])



ingredient_views = Blueprint('ingredient_views', __name__, template_folder='../templates')

@ingredient_views.route('/dashboard', methods=['GET', 'POST'])
@jwt_required()
def dashboard():
    """Display the dashboard with local ingredient list and inventory."""
    user_id   = get_jwt_identity()
    query     = request.form.get('query', '').lower()
    show_all  = request.form.get('show_all')

    # 🔄 Load from local JSON instead of external API
    json_path = os.path.join(os.path.dirname(__file__), 'ingredient_list.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_ingredients = data.get('meals', [])

    # ✅ Filter logic: if no "show_all" and a query was submitted, filter—
    # otherwise show all
    if not show_all and query:
        search_results = [
            ing for ing in all_ingredients
            if query in ing['strIngredient'].lower()
        ]
    else:
        search_results = all_ingredients

    # TODO: pull from your DB here
    user_ingredients = []

    return render_template(
        'dashboard.html',
        search_results=search_results,
        user_ingredients=user_ingredients
    )

@ingredient_views.route('/ingredients/add', methods=['POST'])
@jwt_required()
def add_ingredient_view():
    """Add an ingredient to the user's inventory."""
    user_id = get_jwt_identity()
    ingredient_id = request.form.get('ingredient_id')
    name = request.form.get('name')
    quantity = int(request.form.get('quantity', 1))
    add_ingredient_to_user(user_id, ingredient_id, name, quantity)
    flash('Ingredient added successfully.')
    return redirect(url_for('ingredient_views.dashboard'))

@ingredient_views.route('/ingredients/remove', methods=['POST'])
@jwt_required()
def remove_ingredient_view():
    """Remove an ingredient from the user's inventory."""
    user_id = get_jwt_identity()
    ingredient_id = request.form.get('ingredient_id')
    success = remove_ingredient_from_user(user_id, ingredient_id)
    if success:
        flash('Ingredient removed successfully.')
    else:
        flash('Ingredient not found.')
    return redirect(url_for('ingredient_views.dashboard'))

@ingredient_views.route('/inventory', methods=['GET', 'POST'])
@jwt_required()
def view_inventory():
    """View and manage the user's inventory."""
    user_id = get_jwt_identity()
    if request.method == 'POST':
        ingredient_id = request.form.get('ingredient_id')
        quantity = int(request.form.get('quantity', 1))
        update_ingredient_quantity(user_id, ingredient_id, quantity)
        flash('Quantity updated successfully.')
    ingredients = get_user_ingredients(user_id)
    return render_template('inventory.html', ingredients=ingredients)

@ingredient_views.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout the user and redirect to the landing page."""
    unset_jwt_cookies
    flash('You have been logged out.')
    return redirect(url_for('index.html'))  