from flask import Blueprint, jsonify
from joblib import load
from sqlalchemy import select, func
from database import db, Center, User, Physician, UserPhysicianAssociation
from flask_login import login_required, current_user
from datetime import date, datetime
import googlemaps
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from dotenv import load_dotenv
import os
import functools

match_routes = Blueprint('match', __name__, url_prefix='/user/current/')

load_dotenv()
gmaps = googlemaps.Client(key=os.environ['GOOGLE_MAP_API_KEY'])

MLR_model = load('./models/logistic_regression.joblib')

def calculate_age(DoB):
    today = date.today()
    return today.year - DoB.year - ((today.month, today.day) < (DoB.month, DoB.day))


def filter_attributes(patient, physician=None):
    patient_dict = patient.to_dict(only=(
        'attribute1', 'attribute2', 'attribute3', 'attribute4', 'attribute5',
        'max_travel_time', 'preferred_transportation', 'address', 'DoB'))

    patient_dict["age"] = calculate_age(patient.DoB)
    if physician:
        patient_dict["match"] = physician.id

    # Calculate longitude and latitude from address
    location = gmaps.geocode(patient_dict["address"])[0]['geometry']['location']
    patient_dict["longitude"] = location["lng"]
    patient_dict["latitude"] = location["lat"]

    patient_dict.pop("address")
    patient_dict.pop("DoB")

    return patient_dict


@match_routes.route("/KNN-match", methods=['GET'])
@login_required
def match_knn():
    # Filter centers by user age and insurance
    user_age = calculate_age(current_user.DoB)
    if user_age >= 18:
        centers = filter(lambda x: x.type in ['adult', "whole_life"], current_user.insurance.covers)
    else:
        centers = filter(lambda x: x.type in ['pediatric', "whole_life"], current_user.insurance.covers)

    # Get all patients of filtered centers
    relevant_patients = []
    for center in centers:
        for physician in center.physicians:
            current_associations = filter(lambda association: association.currently_visiting, physician.patient_associations)
            relevant_patients += [filter_attributes(association.user, physician) for association in current_associations]

    # Get age, attributes, preferred_transportation, maximum_travel_time, longitude, latitude for each patient
    data = pd.DataFrame.from_records(relevant_patients + [filter_attributes(current_user)])

    # One-hot encode categorical variables and normalize numeric variables
    data = pd.get_dummies(data, columns=['preferred_transportation'])

    numeric_data = data[['attribute1', 'attribute2', 'attribute3', 'attribute4', 'attribute5',
                         'max_travel_time', 'latitude', 'longitude']]
    normalized_data = (numeric_data - numeric_data.iloc[:-1].mean(numeric_only=True)) / numeric_data.iloc[:-1].std(numeric_only=True)
    data[['attribute1', 'attribute2', 'attribute3', 'attribute4', 'attribute5',
          'max_travel_time', 'latitude', 'longitude']] = normalized_data

    # print(data.to_string())

    # Set up KNN
    model = KNN(n_neighbors=1)
    model.fit(data.drop('match', axis=1).iloc[:-1].to_numpy(), data['match'].iloc[:-1].to_numpy())

    # Find center_id of match
    match_id = model.predict(data.drop('match', axis=1).iloc[-1].to_numpy().reshape(1, -1))

    matched_physician = db.get_or_404(Physician, match_id)
    response = matched_physician.to_dict(rules=("-patient_associations",))
    response.update(travel_time(current_user.address, matched_physician.center.address))
    return response


def reformat_for_matching(user):
    user_dict = user.to_dict(only=(
        'attribute1', 'attribute2', 'attribute3', 'attribute4', 'attribute5',
        'max_travel_time', 'preferred_transportation', 'address', 'DoB', 'insurance'))

    user_dict["age"] = calculate_age(user.DoB)

    # Calculate longitude and latitude from address
    location = gmaps.geocode(user_dict["address"])[0]['geometry']['location']
    user_dict["lng"] = location["lng"]
    user_dict["lat"] = location["lat"]

    user_dict[f"preferred_transportation_{user_dict['preferred_transportation']}"] = True
    user_dict[f"insurance_{user_dict['insurance']['name']}"] = True

    user_dict.pop('preferred_transportation')
    user_dict.pop('insurance')
    user_dict.pop("address")
    user_dict.pop("DoB")

    columns = ['max_travel_time', 'attribute1', 'attribute2', 'attribute3',
               'attribute4', 'attribute5', 'age', 'lng', 'lat',
               'preferred_transportation_driving',
               'preferred_transportation_transit', 'insurance_aetna',
               'insurance_anthem_inc',
               'insurance_blue_cross_blue_shield_association',
               'insurance_centene_corporation', 'insurance_cigna',
               'insurance_health_care_service_corporation', 'insurance_humana',
               'insurance_kaiser_permanente', 'insurance_molina_healthcare',
               'insurance_unitedhealth_group']

    series = pd.Series(user_dict)

    for column in columns:
        if column not in series:
            series[column] = False

    return series.reindex(columns)


@match_routes.route("/score-match", methods=['GET'])
@login_required
def get_matches():
    associations = list(filter(lambda association: association.match_score, current_user.physician_associations))

    if len(associations) == 0:
        associations = match_by_score()
    else:
        associations.sort(key=lambda x: x.match_score, reverse=True)

    scores = [association.match_score for association in associations]
    scores = [(score - min(scores)) / (max(scores) - min(scores)) * 5 for score in scores]

    print(scores)

    def association_to_dict(association, score):
        result = association.physician.to_dict()
        result.update(association.to_dict(only=("visited", "currently_visiting", "saved")))
        result["match_score"] = score
        return result

    return [association_to_dict(association[0], association[1]) for association in zip(associations, scores)]


def match_by_score():
    # Run match
    user = reformat_for_matching(current_user)
    log_prob = MLR_model.predict_log_proba(user.to_frame().T)[0]
    physician_scores = list(zip(MLR_model.classes_, log_prob))

    # Store each user physician pair into the database
    for score in physician_scores:
        generate_association(score)
    db.session.commit()

    return current_user.physician_associations


def generate_association(physician_score):
    physician_id, score = physician_score
    db.session.merge(UserPhysicianAssociation(user_id=current_user.id, physician_id=physician_id, match_score=score))


def travel_time(address1, address2, mode=None):
    if mode:
        if type(address1) == str and type(address2) == str:
            try:
                return gmaps.distance_matrix(address1, address2, mode, units="imperial")['rows'][0]['elements'][0]['duration']['value']
            except KeyError:
                print("Error: {address1} {address2}")
                return 0
        matrix = []
        response = gmaps.distance_matrix(address1, address2, mode, units="imperial")
        for row in response['rows']:
            arr = []
            for element in row['elements']:
                arr.append(element['duration']['value'] if 'duration' in element else 0)
            matrix.append(arr)
        return matrix

    times = []
    for mode in ["driving", "walking", "bicycling", "transit"]:
        try:
            time = gmaps.distance_matrix(address1, address2, mode, units="imperial")['rows'][0]['elements'][0]['duration']['value']
        except KeyError:
            time = -1
        times.append((mode, time))
    return dict(times)
