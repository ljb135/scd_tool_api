from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Double, Date, Column, ForeignKey, Float, Table, Boolean
from flask_login import UserMixin
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy_serializer import SerializerMixin
from dataclasses import dataclass

db = SQLAlchemy()


@dataclass
class User(db.Model, UserMixin, SerializerMixin):
    serialize_rules = ('-physician_associations', '-insurance.users', '-insurance.covers', '-insurance_id', '-reviews', '-symptoms')

    id: int = Column(Integer, primary_key=True)
    email: str = Column(String(50), unique=True, nullable=False)
    password: str = Column(String(50), nullable=False)
    first_name: str = Column(String(30), nullable=False)
    last_name: str = Column(String(30), nullable=False)
    DoB: str = Column(Date, unique=False, nullable=False)
    phone_number: str = Column(String(20), unique=True, nullable=False)

    ethnicity: str = Column(String(20))
    address: str = Column(String(200), unique=False, nullable=False)
    income: int = Column(Integer)
    education: str = Column(String(30))

    preferred_transportation: str = Column(String(10))
    max_travel_time: int = Column(Integer)

    attribute1: float = Column(Double)
    attribute2: float = Column(Double)
    attribute3: float = Column(Double)
    attribute4: float = Column(Double)
    attribute5: float = Column(Double)

    insurance_id: int = Column(ForeignKey("insurance.id"))
    insurance: Mapped['Insurance'] = relationship(back_populates="users")

    physician_associations: Mapped[List['UserPhysicianAssociation']] = relationship(back_populates="user")

    reviews: Mapped[List['Review']] = relationship(back_populates="user")

    symptoms: Mapped[List['DailySymptoms']] = relationship(back_populates="user")


coverage_table = Table(
    "coverage_table",
    db.metadata,
    Column("insurance_id", ForeignKey("insurance.id"), primary_key=True),
    Column("center_id", ForeignKey("center.id"), primary_key=True),
)


@dataclass
class UserPhysicianAssociation(db.Model, SerializerMixin):
    user_id: int = Column(ForeignKey("user.id"), primary_key=True)
    user: Mapped['User'] = relationship(back_populates="physician_associations")

    physician_id: int = Column(ForeignKey("physician.id"), primary_key=True)
    physician: Mapped['Physician'] = relationship(back_populates="patient_associations")

    match_score: float = Column(Float)
    currently_visiting: bool = Column(Boolean)
    visited: bool = Column(Boolean)
    saved: bool = Column(Boolean)


@dataclass
class Center(db.Model, SerializerMixin):
    serialize_rules = ('-physicians.center', '-physicians.patients', '-insurances.users', '-insurances.covers')

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), unique=True, nullable=False)
    address: str = Column(String(200), unique=True, nullable=False)
    type: str = Column(String(10), nullable=False)
    email: str = Column(String(30))
    phone_number: str = Column(String(20))
    website: str = Column(String(250))
    reviews: float = Column(Float)
    image_link: str = Column(String(500))

    physicians: Mapped[List['Physician']] = relationship(back_populates='center')
    insurances: Mapped[List['Insurance']] = relationship(secondary=coverage_table, back_populates='covers')
    

@dataclass
class Physician(db.Model, SerializerMixin):
    serialize_rules = ('-center.physicians', '-patient_associations', '-reviews', 'avg_user_rating', 'avg_attr')

    def avg_user_rating(self):
        reviews = self.reviews
        return sum(review.physician_score for review in reviews) / len(reviews) if len(reviews) > 0 else 0

    def avg_attr(self):
        reviews = self.reviews
        attrs = {}
        for i in range(1, 6):
            attrs[f"attribute{i}"] = sum(review.__getattribute__(f"attribute{i}") for review in reviews) / len(reviews) if len(reviews) > 0 else 0
        return attrs

    id: int = Column(Integer, primary_key=True)
    first_name: str = Column(String(30), nullable=False)
    last_name: str = Column(String(30), nullable=False)
    DoB: str = Column(Date, unique=False, nullable=False)
    ethnicity: str = Column(String(20))
    title: str = Column(String(40))
    additional_language: str = Column(String(40))
    image_link: str = Column(String(500))

    patient_associations: Mapped[List["UserPhysicianAssociation"]] = relationship(back_populates="physician")

    center_id: int = Column(ForeignKey("center.id"))
    center: Mapped['Center'] = relationship(back_populates='physicians')
    
    reviews: Mapped[List["Review"]] = relationship(back_populates="physician")


@dataclass
class Review(db.Model, SerializerMixin):
    serialize_rules = ('-user.reviews', '-physician.reviews')
    
    id: int = Column(Integer, primary_key=True)
    physician_score: int = Column(Integer, nullable=False)
    comment_to_physician: str = Column(String(100), nullable=True)

    attribute1: float = Column(Double, nullable=True)
    attribute2: float = Column(Double, nullable=True)
    attribute3: float = Column(Double, nullable=True)
    attribute4: float = Column(Double, nullable=True)
    attribute5: float = Column(Double, nullable=True)
    
    physician_id: int = Column(ForeignKey("physician.id"))
    physician: Mapped["Physician"] = relationship(back_populates="reviews")

    user_id: int = Column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="reviews")
    

@dataclass
class Insurance(db.Model, SerializerMixin):
    serialize_rules = ('-user.insurance', '-center.insurances')

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(50), unique=True, nullable=False)

    users: Mapped[List['User']] = relationship(back_populates='insurance')
    covers: Mapped[List['Center']] = relationship(secondary=coverage_table, back_populates='insurances')

@dataclass
class DailySymptoms(db.Model, SerializerMixin):
    serialize_rules = ("-user",)

    date: str = Column(Date, unique=False, primary_key=True)

    user_id: int = Column(ForeignKey("user.id"), primary_key=True)
    user: Mapped['User'] = relationship(back_populates="symptoms")

    fever: bool = Column(Boolean)
    chest_pain: bool = Column(Boolean)
    coughing: bool = Column(Boolean)
    shortness_of_breath: bool = Column(Boolean)
    fatigue: bool = Column(Boolean)
    swelling: bool = Column(Boolean)
    jaundice: bool = Column(Boolean)
    numbness: bool = Column(Boolean)
    confusion: bool = Column(Boolean)
    priapism: bool = Column(Boolean)
