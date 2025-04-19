from flask import Blueprint, render_template, jsonify, request, flash, session, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from App.models import User
from App.database import db
from App.controllers.user import create_user, get_all_users
from App.views.ingredient import ingredient_views

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''

@auth_views.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity=user.id)
            resp = redirect(url_for('ingredient_views.dashboard'))  
            set_access_cookies(resp, access_token)
            return resp

        flash('Invalid credentials')

    return render_template('auth/login.html')

@auth_views.route('/logout', methods=['GET'])
def logout():
    response = redirect(url_for('auth_views.login'))
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

@auth_views.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        raw_password = request.form['password']
        hashed_password = generate_password_hash(raw_password)

        new_user = create_user(username, hashed_password)
        flash('Account created successfully!')
        return redirect(url_for('auth_views.login'))

    return render_template('auth/signup.html')

'''
Helper Function
'''

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return create_access_token(identity=user.id)
    return None

'''
API Routes
'''
