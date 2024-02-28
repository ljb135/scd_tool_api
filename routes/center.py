from flask import Blueprint, request, Response, jsonify
from sqlalchemy import select
from database import db, User
from flask_login import login_required

center_routes = Blueprint('center', __name__, url_prefix='/centers')

@center_routes.route("/scored", methods=['GET'])
def getScoredCenters():
    center_data = [{
        "id:": 1,
        "name": "Mayo Clinic",
        "address": "1234 Main St",
    },
    {
        "id:": 2,
        "name": "Harvard Brigham and Women's Comprehensive Sickle Cell Center",
        "address": "3456 Elm St",
    },
    {
        "id:": 3,
        "name": "University of Rochester Pediatric Sickle Cell Program",
        "address": "131 Main St",
    },
    {
        "id:": 4,
        "name": "The Sickle Cell Center of Levine Cancer Institute",
        "address": "983 Elm St",
    },
    {
        "id:": 5,
        "name": "New England Sickle Cell Institute",
        "address": "129 Main St",
    },
    {
        "id:": 6,
        "name": "Columbia University Irving Medical Center/Children's Hospital of New York-Presbyterian",
        "address": "0926 Elm St",
    },
    {
        "id:": 7,
        "name": "Prisma Health Comprehensive Lifespan SCD Program",
        "address": "75 Main St",
    }]
    return jsonify(center_data)

@center_routes.route("/similar", methods=['GET'])
def getSimilarCenter():
    center_data = {
        "id:": 8,
        "name": "RWJ Cancer Institute",
        "address": "1 Robert Wood Johnson Pl, New Brunswick, NJ 08901",
    }
    return jsonify(center_data)

