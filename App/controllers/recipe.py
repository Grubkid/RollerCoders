import requests
from App.controllers.ingredient import get_user_ingredients
from App.models.recipe import Recipe
from App.models.user_recipe import UserRecipe
from App.database import db

def fetch_meals_by_ingredient(ingredient):
    """Return list of {idMeal, strMeal, strMealThumb} for a given ingredient."""
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
    res = requests.get(url)
    if res.ok:
        return res.json().get('meals') or []
    return []

def lookup_full_recipe(id_meal):
    """Return full meal object including all strIngredient/strMeasure pairs."""
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={id_meal}"
    res = requests.get(url)
    meals = res.json().get('meals')
    return meals[0] if meals else None

def search_recipes_for_user(user_id):
    """
    Search TheMealDB for any recipe containing ingredients in the user's inventory.
    Returns a dict of idMeal → full recipe details.
    """
    user_ings = get_user_ingredients(user_id)   # [{'ingredient_id':..., 'name':'Chicken', 'quantity':2}, …]
    found = {}

    for ing in user_ings:
        name = ing['name']
        # fetch minimal info by ingredient
        meals = fetch_meals_by_ingredient(name)
        for m in meals:
            mid = m['idMeal']
            # avoid duplicate lookups
            if mid not in found:
                full = lookup_full_recipe(mid)
                if full:
                    found[mid] = full

    return list(found.values())

def save_recipe_for_user(user_id, recipe_data):
    existing = Recipe.query.filter_by(api_recipe_id=recipe_data['idMeal']).first()

    if not existing:
        # parse ingredients into list of {"ingredient": str, "measure": str}
        ingredients = []
        for i in range(1, 21):
            ing = recipe_data.get(f"strIngredient{i}")
            meas = recipe_data.get(f"strMeasure{i}")
            if ing and ing.strip():
                ingredients.append({"ingredient": ing.strip(), "measure": meas.strip() if meas else ""})

        existing = Recipe(
            api_recipe_id = recipe_data['idMeal'],
            name          = recipe_data['strMeal'],
            category      = recipe_data.get('strCategory'),
            area          = recipe_data.get('strArea'),
            instructions  = recipe_data.get('strInstructions'),
            thumbnail     = recipe_data.get('strMealThumb'),
            tags          = recipe_data.get('strTags', '').split(',') if recipe_data.get('strTags') else [],
            youtube_url   = recipe_data.get('strYoutube'),
            source_url    = recipe_data.get('strSource'),
            date_modified = recipe_data.get('dateModified'),
            ingredients   = ingredients
        )
        db.session.add(existing)
        db.session.commit()

    # check if already saved
    link = UserRecipe.query.filter_by(user_id=user_id, recipe_id=existing.id).first()
    if not link:
        link = UserRecipe(user_id=user_id, recipe_id=existing.id)
        db.session.add(link)
        db.session.commit()
        return True
    return False

def get_saved_recipes(user_id):
    saved = UserRecipe.query.filter_by(user_id=user_id).all()
    return [s.recipe.to_dict() for s in saved]

def remove_saved_recipe(user_id, recipe_id):
    saved = UserRecipe.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    if saved:
        db.session.delete(saved)
        db.session.commit()
        return True
    return False


def get_all_categories():
    url = 'https://www.themealdb.com/api/json/v1/1/list.php?c=list'
    res = requests.get(url)
    if res.ok:
        return [c['strCategory'] for c in res.json().get('meals', [])]
    return []

def get_all_areas():
    url = 'https://www.themealdb.com/api/json/v1/1/list.php?a=list'
    res = requests.get(url)
    if res.ok:
        return [a['strArea'] for a in res.json().get('meals', [])]
    return []
