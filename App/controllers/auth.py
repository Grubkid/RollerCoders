from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request

from App.models import User
from App.database import db

def login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return create_access_token(identity=str(user.id))  # Ensure identity is a string
    return None

def create_user(username, password):
    if User.query.filter_by(username=username).first():
        return None
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

def setup_jwt(app):
  jwt = JWTManager(app)

  # configure's flask jwt to resolve get_current_identity() to the corresponding user's ID
  @jwt.user_identity_loader
  def user_identity_lookup(identity):
    return str(identity)  # Ensure identity is always a string

  @jwt.user_lookup_loader
  def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.get(identity)

  return jwt


# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request()
          user_id = str(get_jwt_identity())
          current_user = User.query.get(user_id)
          is_authenticated = True
      except Exception as e:
          print(e)
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)