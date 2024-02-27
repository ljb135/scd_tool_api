from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, Date, Column, ForeignKey
from dataclasses import dataclass
from flask_login import UserMixin
from sqlalchemy.orm import relationship, Mapped

db = SQLAlchemy()

@dataclass
class User(UserMixin, db.Model):
    id: int = Column(Integer, primary_key=True)
    email: str = Column(String(30), unique=True, nullable=False)
    password: str = Column(String(30), nullable=False)
    first_name: str = Column(String(30), nullable=False)
    last_name: str = Column(String(30), nullable=False)
    DoB: str = Column(Date, unique=False, nullable=False)
    phone_number: int = Column(Integer, unique=True, nullable=False)
    ethnicity: str = Column(String(10))
    address: str = Column(String(60), unique=False, nullable=False)
    insurance: str = Column(String(30))
    income: int = Column(Integer)
    education: str = Column(String(30))
    treatment_id: int = Column(ForeignKey("treatment.id"))
    treatment: Mapped['Treatment'] = relationship(back_populates="patients")


@dataclass
class Center(db.Model):
    id: int = Column(Integer, primary_key=True)
    address: str = Column(String(60), unique=True, nullable=False)
    google_review: str = Column(String(150))
    email: str = Column(String(30), unique=True, nullable=False)
    phone_number: int = Column(Integer, unique=True, nullable=False)

    treatments: Mapped[List['Treatment']] = relationship(back_populates='center')


@dataclass
class Treatment(db.Model):
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(30), unique=True, nullable=False)
    type: str = Column(String(30), nullable=False)  # Integer?
    # duration = Column(String(30), nullable=False)  # date time? Integer (in days or hours)

    patients: Mapped[List['User']] = relationship(back_populates='treatment')
    center_id: int = Column(ForeignKey("center.id"))
    center: Mapped['Center'] = relationship(back_populates='treatments')


@dataclass
class Insurance(db.Model):
    id = Column(Integer, primary_key=True)
    Name = Column(String(30), nullable=False)
    company = Column(String(20), nullable=False)
    coverage = Column(Boolean)
