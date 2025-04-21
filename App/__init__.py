from flask import Flask
from App.database import db, get_migrate
from App.controllers.ingredient import ingredient_views
from App.views.ingredient import ingredient_views
from App.views.auth import auth_views
from App.cache import preload_categories, preload_areas

preload_categories()
preload_areas()
def create_app():
    app = Flask(__name__)
    db.init_app(app)
    migrate = get_migrate()
    migrate.init_app(app, db)

   
    app.register_blueprint(ingredient_views)
    app.register_blueprint(auth_views)


    return app