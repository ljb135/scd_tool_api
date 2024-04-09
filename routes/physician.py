from flask import Blueprint, Response, request
from sqlalchemy import select, func
from itertools import chain
from database import db, Physician, Review
from flask_login import login_required, current_user

physician_routes = Blueprint('physician', __name__, url_prefix='/physician')


@physician_routes.route("", methods=['GET'])
def get_all_physicians():
    physicians = db.session.query(Physician).limit(10).all()
    return [physician.to_dict() for physician in physicians]


@physician_routes.route("/<int:physician_id>", methods=['GET'])
def get_physician(physician_id):
    physician = db.get_or_404(Physician, physician_id)
    return physician.to_dict()


@physician_routes.route("/<int:physician_id>/review", methods=['POST'])
@login_required
def add_review(physician_id):
    review_json = request.json
    review_json["user_id"] = current_user.id
    review_json["physician_id"] = physician_id
    review = Review(**review_json)
    db.session.add(review)
    db.session.commit()
    return Response("Review has been created.", status=201)
