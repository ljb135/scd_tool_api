from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import json
from database import User, Center, Insurance, Physician, Review

engine = create_engine(
    "mysql+pymysql://v02uazsj0uc9txhv16fu:pscale_pw_3787lvNnmOePNpDb0OH3qJXV1u96Ysrn35uugaVBcxN@aws.connect.psdb.cloud/scd_tool?ssl={'rejectUnauthorized':true}&ssl_ca=../cacert.pem")


def create_insurance_from_json(insurance_json):
    return Insurance(**insurance_json)


def create_center_from_json(center_json):
    center_json["insurances"] = session.query(Insurance).filter(Insurance.name.in_(center_json["insurances"].split(", "))).all()
    return Center(**center_json)


def create_physician_from_json(physician_json):
    physician_json["center"] = session.scalars(select(Center).filter_by(name=physician_json["center"])).first()
    return Physician(**physician_json)


def create_user_from_json(user_json):
    user_json["insurance"] = session.scalars(select(Insurance).filter_by(name=user_json["insurance"])).first()
    user_json["physician"] = session.scalars(select(Physician).filter_by(center=session.scalars(select(Center).filter_by(name=user_json['physician'])).first())).first()
    return User(**user_json)


def create_review_from_json(review_json):
    return Review(**review_json)


session = Session(engine)
# print(session.scalars(select(Treatment).filter_by(type='prescribe_voxeletor')).first().center)

data = json.load(open('data.json'))
# session.add_all([create_insurance_from_json(insurance) for insurance in data['Insurance_Data']])
# session.add_all([create_center_from_json(center) for center in data['Center_Data']])
# session.add_all([create_physician_from_json(physician) for physician in data['Physician_Data']])
# session.add_all([create_user_from_json(user) for user in data['User_Data']])
session.add_all([create_review_from_json(review) for review in data['Review_Data']])
session.commit()
