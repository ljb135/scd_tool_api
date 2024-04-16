from datetime import datetime

from flask import Blueprint, request, Response, jsonify
from sqlalchemy import select
from database import db, User, Insurance, UserPhysicianAssociation, DailySymptoms
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


@user_routes.route("/current/accessible-physician", methods=['GET'])
@login_required
def get_physicians_for_current_user():
    centers = current_user.insurance.covers
    return [physician.to_dict() for center in centers for physician in list(center.physicians)]


@user_routes.route("/current/saved-physician", methods=['GET'])
@login_required
def get_saved_physicians_for_current_user():
    def association_to_dict(association):
        result = association.physician.to_dict()
        result.update(association.to_dict(only=("visited", "currently_visiting", "saved", "match_score")))
        return result

    associations = filter(lambda association: association.saved, current_user.physician_associations)
    return [association_to_dict(association) for association in associations]


@user_routes.route("/current/saved-physician/<int:physician_id>", methods=['PUT'])
@login_required
def update_saved_physicians_for_current_user(physician_id):
    db.session.merge(UserPhysicianAssociation(user_id=current_user.id, physician_id=physician_id, saved=True))
    db.session.commit()
    return Response("Physician saved.", status=200)


@user_routes.route("/current/saved-physician/<int:physician_id>", methods=['DELETE'])
@login_required
def delete_saved_physicians_for_current_user(physician_id):
    db.session.merge(UserPhysicianAssociation(user_id=current_user.id, physician_id=physician_id, saved=False))
    db.session.commit()
    return Response("Physician unsaved.", status=200)


@user_routes.route("/current/visited-physician/<int:physician_id>", methods=['PUT'])
@login_required
def update_visited_physicians_for_current_user(physician_id):
    db.session.merge(UserPhysicianAssociation(user_id=current_user.id, physician_id=physician_id, visited=True))
    db.session.commit()
    return Response("Physician visited.", status=200)


@user_routes.route("/current/visited-physician/<int:physician_id>", methods=['DELETE'])
@login_required
def delete_visited_physicians_for_current_user(physician_id):
    db.session.merge(UserPhysicianAssociation(user_id=current_user.id, physician_id=physician_id, visited=False))
    db.session.commit()
    return Response("Physician unvisited.", status=200)


@user_routes.route("/current/accessible-center", methods=['GET'])
@login_required
def get_centers_for_current_user():
    centers = current_user.insurance.covers
    return [center.to_dict() for center in centers]


@user_routes.route("/current/daily-symptoms", methods=['GET'])
@login_required
def get_symptoms_for_current_user():
    symptoms = current_user.symptoms
    return [symptom.to_dict() for symptom in symptoms]


@user_routes.route("/current/daily-symptoms", methods=['PUT'])
@login_required
def add_symptoms_for_current_user():
    symptoms_json = request.json
    symptoms_json["user_id"] = current_user.id
    if "date" not in symptoms_json:
        symptoms_json["date"] = datetime.now()
    symptoms = DailySymptoms(**symptoms_json)
    db.session.add(symptoms)
    db.session.commit()
    return Response("Symptoms have been logged.", status=201)


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
