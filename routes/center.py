from flask import Blueprint, jsonify
from sqlalchemy import select
from database import db, Center

center_routes = Blueprint('center', __name__, url_prefix='/center')


@center_routes.route("/", methods=['GET'])
def get_all_centers():
    centers = db.session.scalars(select(Center))
    # centers = db.session.execute(select(Center.id, Center.name, Center.address, Center.type, Center.email, Center.phone_number, Center.website, Center.reviews)).all()
    return jsonify(list(centers))


@center_routes.route("/<int:center_id>", methods=['GET'])
def get_center(center_id):
    center = db.get_or_404(Center, center_id)
    print(center)
    return jsonify(center)
