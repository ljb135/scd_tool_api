from flask import Blueprint, request, Response, jsonify
from sqlalchemy import select
from database import db, User
from flask_login import LoginManager, login_user, logout_user

session_routes = Blueprint('session', __name__, url_prefix='/session')
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@session_routes.route("/", methods=['POST'])
def login():
    user = User.query.filter_by(email=request.json.get("email")).first()
    if user and user.password == request.json.get("password"):
        login_user(user)
        return Response("Authentication success.", status=200)
    return Response("Authentication failed.", status=401)


@session_routes.route("/", methods=['DELETE'])
def logout():
    logout_user()
    return Response("Session Destroyed.", status=200)
