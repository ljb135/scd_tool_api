from flask import Blueprint
from database import db, Insurance

insurance_routes = Blueprint('insurance', __name__, url_prefix='/insurance')


@insurance_routes.route("/", methods=['GET'])
def get_all_centers():
    insurances = db.session.query(Insurance).limit(10).all()
    return [insurance.to_dict(only=('id', 'name')) for insurance in insurances]
