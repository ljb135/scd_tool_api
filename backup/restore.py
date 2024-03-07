from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from itertools import chain
import json
from database import User, Center, Treatment, Insurance

engine = create_engine(
    "mysql+pymysql://v02uazsj0uc9txhv16fu:pscale_pw_3787lvNnmOePNpDb0OH3qJXV1u96Ysrn35uugaVBcxN@aws.connect.psdb.cloud/scd_tool?ssl={'rejectUnauthorized':true}&ssl_ca=../cacert.pem")


def create_insurance_from_json(insurance_json):
    return Insurance(**insurance_json)


def create_center_from_json(center_json):
    center_json["insurances"] = session.query(Insurance).filter(Insurance.name.in_(center_json["insurances"].split(", "))).all()
    return Center(**center_json)


def create_treatment_from_json(treatment_json):
    treatment_types = ['crizanlizumab_infusions', 'prescribe_voxeletor', 'pharma_clinical_trials', 'stem_cell_transplant', 'compound_hydroxyurea']
    treatments = []
    for treatment_type in treatment_types:
        if treatment_json[treatment_type] == "TRUE":
            treatments.append(Treatment(type=treatment_type, center_id=session.scalars(select(Center).filter_by(name=treatment_json['center_name'])).first().id))
    return treatments


def create_user_from_json(user_json):
    user_json["insurance"] = session.scalars(select(Insurance).filter_by(name=user_json["insurance"])).first()
    user_json["treatment"] = session.scalars(select(Treatment).filter_by(center=session.scalars(select(Center).filter_by(name=user_json['treatment'])).first())).first()
    return User(**user_json)


session = Session(engine)
# print(session.scalars(select(Treatment).filter_by(type='prescribe_voxeletor')).first().center)

data = json.load(open('data.json'))
session.add_all([create_insurance_from_json(insurance) for insurance in data['Insurance_Data']])
session.add_all([create_center_from_json(center) for center in data['Center_Data']])
session.add_all(list(chain.from_iterable(create_treatment_from_json(treatment) for treatment in data['Treatment_Data'])))
session.add_all([create_user_from_json(user) for user in data['User_Data']])
session.commit()
