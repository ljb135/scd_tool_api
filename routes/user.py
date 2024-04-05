from flask import Blueprint, request, Response, jsonify
from sqlalchemy import select
from database import db, User, Insurance
from flask_login import login_required, current_user

user_routes = Blueprint('user', __name__, url_prefix='/user')


@user_routes.route("", methods=['POST'])
def add_user():
    user_json = request.json
    if "insurance" in user_json:
        user_json["insurance"] = db.session.scalars(select(Insurance).filter_by(name=user_json["insurance"])).first()
    user = User(**user_json)
    db.session.add(user)
    db.session.commit()
    return Response("User has been created.", status=201)


@user_routes.route("", methods=['GET'])
def get_all_users():
    users = db.session.scalars(select(User))
    return [user.to_dict() for user in users]


@user_routes.route("/current", methods=['GET'])
@login_required
def get_current_user():
    return current_user.to_dict()


@user_routes.route("/current", methods=['PUT'])
@login_required
def modify_current_user():
    content = request.json
    for key in content:
        setattr(current_user, key, content[key])
    db.session.commit()
    return Response("User has been updated.", status=200)


@user_routes.route("/current", methods=['DELETE'])
@login_required
def delete_current_user():
    db.session.delete(current_user)
    db.session.commit()
    return Response("User has been deleted.", status=200)


@user_routes.route("/current/accessible-physicians", methods=['GET'])
@login_required
def get_physicians_for_current_user():
    centers = current_user.insurance.covers
    return [physician.to_dict() for center in centers for physician in list(center.physicians)]


@user_routes.route("/current/accessible-centers", methods=['GET'])
@login_required
def get_centers_for_current_user():
    centers = current_user.insurance.covers
    return [center.to_dict() for center in centers]


@user_routes.route("/<int:user_id>", methods=['GET'])
def get_user(user_id):
    user = db.get_or_404(User, user_id)
    return user.to_dict()


@user_routes.route("/<int:user_id>", methods=['PUT'])
def modify_user(user_id):
    content = request.json
    user = db.get_or_404(User, user_id)
    for key in content:
        setattr(user, key, content[key])
    db.session.commit()
    return Response("User has been updated.", status=200)


@user_routes.route("/<int:user_id>", methods=['DELETE'])
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return Response("User has been deleted.", status=200)
