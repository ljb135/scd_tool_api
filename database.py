from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, Date, Column, ForeignKey, Float
from flask_login import UserMixin
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy_serializer import SerializerMixin
from dataclasses import dataclass

db = SQLAlchemy()


@dataclass
class User(db.Model, UserMixin, SerializerMixin):
    serialize_rules = ('-treatment.patients',)

    id: int = Column(Integer, primary_key=True)
    email: str = Column(String(50), unique=True, nullable=False)
    password: str = Column(String(50), nullable=False)
    first_name: str = Column(String(30), nullable=False)
    last_name: str = Column(String(30), nullable=False)
    DoB: str = Column(Date, unique=False, nullable=False)
    phone_number: str = Column(String(20), unique=True, nullable=False)
    ethnicity: str = Column(String(20))
    address: str = Column(String(100), unique=False, nullable=False)
    # insurance: str = Column(String(30))
    income: int = Column(Integer)
    education: str = Column(String(30))
    preferred_transportation: str = Column(String(10))

    treatment_id: int = Column(ForeignKey("treatment.id"))
    treatment: Mapped['Treatment'] = relationship(back_populates="patients")


@dataclass
class Center(db.Model, SerializerMixin):
    serialize_rules = ('-treatments.center',)

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), unique=True, nullable=False)
    address: str = Column(String(200), unique=True, nullable=False)
    type: str = Column(String(10), nullable=False)
    email: str = Column(String(30))
    phone_number: str = Column(String(20))
    website: str = Column(String(250))
    reviews: float = Column(Float)

    treatments: Mapped[List['Treatment']] = relationship(back_populates='center')


@dataclass
class Treatment(db.Model, SerializerMixin):
    serialize_rules = ('-center.treatments', '-user.treatment')

    id: int = Column(Integer, primary_key=True)
    type: str = Column(String(30), nullable=False)  # Integer?
    patients: Mapped[List['User']] = relationship(back_populates='treatment')
    center_id: int = Column(ForeignKey("center.id"))

    center: Mapped['Center'] = relationship(back_populates='treatments')


@dataclass
class Insurance(db.Model, SerializerMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    company = Column(String(20), nullable=False)
    coverage = Column(Boolean)
