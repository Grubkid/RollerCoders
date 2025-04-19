import pytest
from App.models import Ingredient, User
from App.database import db
from App.controllers.ingredient import (
    add_ingredient_to_user,
    remove_ingredient_from_user,
    update_ingredient_quantity,
    get_user_ingredients
)

@pytest.fixture
def setup_user_and_ingredient(app):
    """Fixture to set up a user and an ingredient for testing."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = User(username="testuser", password="testpass")
        db.session.add(user)
        db.session.commit()
        return user

def test_add_ingredient_to_user(app, setup_user_and_ingredient):
    """Test adding an ingredient to a user's inventory."""
    user = setup_user_and_ingredient
    add_ingredient_to_user(user.id, "45", "Canned Tomatoes", 2)
    ingredients = get_user_ingredients(user.id)
    assert len(ingredients) == 1
    assert ingredients[0]["name"] == "Canned Tomatoes"
    assert ingredients[0]["quantity"] == 2

def test_remove_ingredient_from_user(app, setup_user_and_ingredient):
    """Test removing an ingredient from a user's inventory."""
    user = setup_user_and_ingredient
    add_ingredient_to_user(user.id, "45", "Canned Tomatoes", 2)
    success = remove_ingredient_from_user(user.id, "45")
    assert success is True
    ingredients = get_user_ingredients(user.id)
    assert len(ingredients) == 0

def test_update_ingredient_quantity(app, setup_user_and_ingredient):
    """Test updating the quantity of an ingredient in a user's inventory."""
    user = setup_user_and_ingredient
    add_ingredient_to_user(user.id, "45", "Canned Tomatoes", 2)
    update_ingredient_quantity(user.id, "45", 5)
    ingredients = get_user_ingredients(user.id)
    assert ingredients[0]["quantity"] == 5