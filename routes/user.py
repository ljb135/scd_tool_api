from flask import Blueprint, request, Response, jsonify
from sqlalchemy import select
from database import db, User
from flask_login import login_required

user_routes = Blueprint('user', __name__, url_prefix='/user')


@user_routes.route("/", methods=['POST'])
def add_user():
    content = request.json
    user = User(**content)
    db.session.add(user)
    db.session.commit()
    return Response("User has been created.", status=201)


@user_routes.route("/", methods=['GET'])
def get_all_users():
    users = db.session.scalars(select(User))
    return [user.to_dict() for user in users]


@user_routes.route("/<int:user_id>", methods=['GET'])
@login_required
def get_user(user_id):
    user = db.get_or_404(User, user_id)
    return user.to_dict()


@user_routes.route("/<int:user_id>", methods=['PUT'])
@login_required
def modify_user(user_id):
    content = request.json
    user = db.get_or_404(User, user_id)
    for key in content:
        setattr(user, key, content[key])
    db.session.commit()
    return Response("User has been updated.", status=200)


@user_routes.route("/<int:user_id>", methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return Response("User has been deleted.", status=200)
