from flask import Blueprint, jsonify
from sqlalchemy import select, func
from database import db, Physician, Center
from flask_login import login_required, current_user

physician_routes = Blueprint('physician', __name__, url_prefix='/physician')


@physician_routes.route("/", methods=['GET'])
def get_physicians():
    #centers = db.session.scalars(select(Center))
    # to randomly select 10 centers for testing purposes
    #centers = db.session.query(Center).order_by(func.random()).limit(10).all()
    physicians = db.session.query(Physician).limit(10).all()
    return [physician.to_dict() for physician in physicians]