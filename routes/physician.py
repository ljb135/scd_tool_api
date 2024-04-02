from flask import Blueprint, jsonify
from sqlalchemy import select, func
from itertools import chain
from database import db, Physician, Center
from flask_login import login_required, current_user

physician_routes = Blueprint('physician', __name__, url_prefix='/physician')


@physician_routes.route("/", methods=['GET'])
def get_all_physicians():
    physicians = db.session.query(Physician).limit(10).all()
    return [physician.to_dict() for physician in physicians]


@physician_routes.route("/user/current", methods=['GET'])
@login_required
def get_physicians_for_current_user():
    centers = current_user.insurance.covers
    return [physician.to_dict() for center in centers for physician in list(center.physicians)]


@physician_routes.route("/<int:physician_id>", methods=['GET'])
def get_physician(physician_id):
    physician = db.get_or_404(Physician, physician_id)
    return physician.to_dict()
