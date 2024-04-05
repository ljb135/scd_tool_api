from flask import Blueprint, jsonify
from sqlalchemy import select, func
from database import db, Center, User, Physician
from flask_login import login_required, current_user
from datetime import date, datetime
import googlemaps
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from dotenv import load_dotenv
import os

match_routes = Blueprint('match', __name__, url_prefix='/match')

load_dotenv()
gmaps = googlemaps.Client(key=os.environ['GOOGLE_MAP_API_KEY'])


def calculate_age(DoB):
    today = date.today()
    return today.year - DoB.year - ((today.month, today.day) < (DoB.month, DoB.day))


def filter_attributes(patient):
    patient_dict = patient.to_dict(only=(
        'attribute1', 'attribute2', 'attribute3', 'attribute4', 'attribute5',
        'max_travel_time', 'preferred_transportation', 'address', 'physician.id', 'DoB'))

    patient_dict["age"] = calculate_age(patient.DoB)
    patient_dict["match"] = patient_dict["physician"]["id"]

    # Calculate longitude and latitude from address
    location = gmaps.geocode(patient_dict["address"])[0]['geometry']['location']
    patient_dict["longitude"] = location["lng"]
    patient_dict["latitude"] = location["lat"]

    patient_dict.pop("address")
    patient_dict.pop("DoB")
    patient_dict.pop("physician")

    return patient_dict


@match_routes.route("/KNN", methods=['GET'])
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
            relevant_patients += physician.patients

    # Get age, attributes, preferred_transportation, maximum_travel_time, longitude, latitude for each patient
    data = pd.DataFrame.from_records([filter_attributes(patient) for patient in relevant_patients + [current_user]])

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
    response = matched_physician.to_dict(rules=("-patients",))
    response.update(travel_time(current_user.address, matched_physician.center.address))
    return response


@match_routes.route("/score", methods=['GET'])
@login_required
def match_by_score():
    # Run match
    
    # Store each user physician pair into the database

    # Return top 10 centers

    physicians = db.session.query(Physician).limit(10).all()
    return [physician.to_dict() for physician in physicians]


def travel_time(address1, address2, mode=None):
    try:
        if mode:
            if type(address1) == str and type(address2) == str:
                return gmaps.distance_matrix(address1, address2, mode, units="imperial")['rows'][0]['elements'][0]['duration']['value']
            matrix = []
            response = gmaps.distance_matrix(address1, address2, mode, units="imperial")
            for row in response['rows']:
                arr = []
                for element in row['elements']:
                    arr.append(element['duration']['value'] if 'duration' in element else 0)
                matrix.append(arr)
            return matrix
        return dict([(mode, gmaps.distance_matrix(address1, address2, mode, units="imperial")['rows'][0]['elements'][0]['duration']['value']) for mode in ["driving", "walking", "bicycling", "transit"]])
    except KeyError:
        print(address1, address2)
        return 0