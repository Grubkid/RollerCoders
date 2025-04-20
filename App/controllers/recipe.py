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
