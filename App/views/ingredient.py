from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user, unset_jwt_cookies
import os, json

from App.controllers.ingredient import (
    add_ingredient_to_user,
    remove_ingredient_from_user,
    update_ingredient_quantity,
    get_user_ingredients,
)

ingredient_views = Blueprint('ingredient_views', __name__, template_folder='../templates')

# Path to local JSON master ingredient list
JSON_PATH = os.path.join(os.path.dirname(__file__), 'ingredient_list.json')

@ingredient_views.route('/dashboard', methods=['GET', 'POST'])
@jwt_required()
def dashboard():
    """Display the dashboard with local ingredient list and the user’s inventory."""
    user_id = get_jwt_identity()

    # Load master ingredient list
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        all_ingredients = json.load(f).get('meals', [])

    # Determine if this is a search (POST) or a “show all” toggle (GET)
    if request.method == 'POST':
        query    = request.form.get('query', '').strip().lower()
        show_all = request.form.get('show_all') == '1'
    else:
        query    = ''
        show_all = request.args.get('show_all') == '1'

    # Filter if searching and not “show all”
    if query and not show_all:
        search_results = [
            ing for ing in all_ingredients
            if query in ing['strIngredient'].lower()
        ]
        if not search_results:
            flash(f"BigBack{current_user.username}, '{query}' is not available for search.", 'error')
    else:
        search_results = all_ingredients

    # Pull the user’s saved ingredients from the DB
    user_ingredients = get_user_ingredients(user_id)

    return render_template(
        'dashboard.html',
        search_results=search_results,
        user_ingredients=user_ingredients
    )

@ingredient_views.route('/ingredients/add', methods=['POST'])
@jwt_required()
def add_ingredient_view():
    """Add an ingredient to the user's inventory."""
    user_id       = get_jwt_identity()
    ingredient_id = request.form.get('ingredient_id')
    name          = request.form.get('name')
    quantity      = int(request.form.get('quantity', 1))

    add_ingredient_to_user(user_id, ingredient_id, name, quantity)
    flash('Ingredient added successfully.', 'success')
    return redirect(url_for('ingredient_views.dashboard'))

@ingredient_views.route('/ingredients/remove', methods=['POST'])
@jwt_required()
def remove_ingredient_view():
    """Decrement an ingredient's quantity, or remove it entirely if it hits zero."""
    user_id       = get_jwt_identity()
    ingredient_id = request.form.get('ingredient_id')

    # Fetch current inventory for this user
    user_ings = get_user_ingredients(user_id)
    # Find the matching ingredient record
    ing = next((i for i in user_ings if i['ingredient_id'] == ingredient_id), None)

    if not ing:
        flash('Ingredient not found in your inventory.', 'error')
        return redirect(url_for('ingredient_views.dashboard'))

    new_qty = ing['quantity'] - 1
    if new_qty > 0:
        # Just decrement
        update_ingredient_quantity(user_id, ingredient_id, new_qty)
        flash(f"Decreased {ing['name']} to {new_qty}.", 'success')
    else:
        # Quantity hit zero: delete record
        remove_ingredient_from_user(user_id, ingredient_id)
        flash(f"Removed all of {ing['name']} from your inventory.", 'success')

    return redirect(url_for('ingredient_views.dashboard'))

@ingredient_views.route('/inventory', methods=['GET', 'POST'])
@jwt_required()
def view_inventory():
    """View and manage the user's inventory."""
    user_id = get_jwt_identity()

    if request.method == 'POST':
        ingredient_id = request.form.get('ingredient_id')
        quantity      = int(request.form.get('quantity', 1))
        if update_ingredient_quantity(user_id, ingredient_id, quantity):
            flash('Quantity updated successfully.', 'success')
        else:
            flash('Could not update quantity.', 'error')

    ingredients = get_user_ingredients(user_id)
    return render_template('inventory.html', ingredients=ingredients)

@ingredient_views.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout the user and redirect to the landing page."""
    unset_jwt_cookies
    flash('You have been logged out.', 'success')
    return redirect(url_for('index_views.index_page'))