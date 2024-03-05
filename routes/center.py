from flask import Blueprint, jsonify
from sqlalchemy import select, func
from database import db, Center
from flask_login import login_required, current_user

center_routes = Blueprint('center', __name__, url_prefix='/center')


@center_routes.route("/", methods=['GET'])
def get_all_centers():
    #centers = db.session.scalars(select(Center))
    # to randomly select 10 centers for testing purposes
    centers = db.session.query(Center).order_by(func.random()).limit(10).all()
    return [center.to_dict() for center in centers]


@center_routes.route("/user/current", methods=['GET'])
@login_required
def get_centers_for_current_user():
    centers = current_user.insurance.covers
    return [center.to_dict() for center in centers]


@center_routes.route("/<int:center_id>", methods=['GET'])
def get_center(center_id):
    center = db.get_or_404(Center, center_id)
    return center.to_dict()
