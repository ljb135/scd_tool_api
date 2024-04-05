from flask import Blueprint, jsonify
from sqlalchemy import select
from database import db, Center
from flask_login import login_required, current_user

center_routes = Blueprint('center', __name__, url_prefix='/center')


@center_routes.route("", methods=['GET'])
def get_all_centers():
    centers = db.session.scalars(select(Center))
    return [center.to_dict() for center in centers]


@center_routes.route("/<int:center_id>", methods=['GET'])
def get_center(center_id):
    center = db.get_or_404(Center, center_id)
    return center.to_dict()