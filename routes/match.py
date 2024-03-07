from flask import Blueprint, jsonify
from sqlalchemy import select, func
from database import db, Center, User
from flask_login import login_required, current_user
from datetime import date, datetime
import googlemaps
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

match_routes = Blueprint('match', __name__, url_prefix='/match')

API_key = "AIzaSyDRSrRqfB6rbE-Ty2c_Ah9-E47FoJVHQ74"
gmaps = googlemaps.Client(key=API_key)


def calculate_age(DoB):
    today = date.today()
    return today.year - DoB.year - ((today.month, today.day) < (DoB.month, DoB.day))


def filter_attributes(patient):
    patient_dict = patient.to_dict(only=(
    'education', 'preferred_transportation', 'address', 'treatment.center.id', 'DoB', 'income'))

    patient_dict["age"] = calculate_age(patient.DoB)
    patient_dict["match"] = patient_dict["treatment"]["center"]["id"]

    # Calculate longitude and latitude from address
    location = gmaps.geocode(patient_dict["address"])[0]['geometry']['location']
    patient_dict["longitude"] = location["lng"]
    patient_dict["latitude"] = location["lat"]

    patient_dict.pop("address")
    patient_dict.pop("DoB")
    patient_dict.pop("treatment")

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
        for treatment in center.treatments:
            relevant_patients += treatment.patients

    # Get income, age, medication, education, preferred_transportation, longitude, latitude for each patient
    data = pd.DataFrame.from_records([filter_attributes(patient) for patient in relevant_patients + [current_user]])

    # One-hot encode categorical variables and normalize numeric variables
    data = pd.get_dummies(data, columns=['education', 'preferred_transportation'])

    numeric_data = data[['income', 'latitude', 'longitude']]
    normalized_data = (numeric_data - numeric_data.iloc[:-1].mean(numeric_only=True)) / numeric_data.iloc[:-1].std(numeric_only=True)
    data[['income', 'latitude', 'longitude']] = normalized_data

    # Set up KNN
    model = KNN(n_neighbors=1)
    model.fit(data.drop('match', axis=1).iloc[:-1].to_numpy(), data['match'].iloc[:-1].to_numpy())

    # Find center_id of match
    match_id = model.predict(data.drop('match', axis=1).iloc[-1].to_numpy().reshape(1, -1))

    return db.get_or_404(Center, match_id).to_dict()
