from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
import json
from database import User, Center, Insurance, Physician, Review, UserPhysicianAssociation

engine = create_engine(
    "mysql+pymysql://v02uazsj0uc9txhv16fu:pscale_pw_3787lvNnmOePNpDb0OH3qJXV1u96Ysrn35uugaVBcxN@aws.connect.psdb.cloud/scd_tool?ssl={'rejectUnauthorized':true}&ssl_ca=../cacert.pem")


def insurance_from_json(insurance_json):
    return Insurance(**insurance_json)


def center_from_json(center_json):
    center_json["insurances"] = session.query(Insurance).filter(Insurance.name.in_(center_json["insurances"].split(", "))).all()
    return Center(**center_json)


def physician_from_json(physician_json):
    physician_json["center"] = session.scalars(select(Center).filter_by(name=physician_json["center"])).first()
    return Physician(**physician_json)


def user_from_json(user_json):
    user_json["insurance"] = session.scalars(select(Insurance).filter_by(name=user_json["insurance"])).first()
    del user_json['physician']
    return User(**user_json)


def user_physician_association_from_json(user_json):
    if "physician" in user_json:
        user = session.scalars(select(User).filter_by(email=user_json['email'])).first()
        physician = session.scalars(select(Physician).filter_by(id=user_json['physician'])).first()
        return UserPhysicianAssociation(user=user, physician=physician, currently_visiting=True, visited=True);
    else:
        return None


def review_from_json(review_json):
    return Review(**review_json)


session = Session(engine)
# print(session.scalars(select(Treatment).filter_by(type='prescribe_voxeletor')).first().center)

data = json.load(open('data.json'))
session.add_all([insurance_from_json(insurance) for insurance in data['Insurance_Data']])
session.add_all([center_from_json(center) for center in data['Center_Data']])
session.add_all([physician_from_json(physician) for physician in data['Physician_Data']])
session.add_all([user_from_json(user) for user in data['User_Data']])
session.add_all([association for association in map(user_physician_association_from_json, data['User_Data']) if association is not None])
session.add_all([review_from_json(review) for review in data['Review_Data']])
session.commit()
