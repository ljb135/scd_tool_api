from typing import List

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean, Date, Column, ForeignKey, Float, Table
from flask_login import UserMixin
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy_serializer import SerializerMixin
from dataclasses import dataclass

db = SQLAlchemy()


@dataclass
class User(db.Model, UserMixin, SerializerMixin):
    serialize_rules = ('-physician.patients', '-insurance.users', '-insurance.covers')

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

    insurance_id: int = Column(ForeignKey("insurance.id"))
    insurance: Mapped['Insurance'] = relationship(back_populates="users")

    physician_id: int = Column(ForeignKey("physician.id"))
    physician: Mapped['Physician'] = relationship(back_populates="patients")


coverage_table = Table(
    "coverage_table",
    db.metadata,
    Column("insurance_id", ForeignKey("insurance.id"), primary_key=True),
    Column("center_id", ForeignKey("center.id"), primary_key=True),
)


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
    serialize_rules = ('-center.physicians', '-patients.physician', '-patients.insurance')

    id: int = Column(Integer, primary_key=True)
    first_name: str = Column(String(30), nullable=False)
    last_name: str = Column(String(30), nullable=False)
    DoB: str = Column(Date, unique=False, nullable=False)
    ethnicity: str = Column(String(20))
    title: str = Column(String(40))
    additional_language: str = Column(String(40))

    patients: Mapped[List['User']] = relationship(back_populates='physician')

    center_id: int = Column(ForeignKey("center.id"))
    center: Mapped['Center'] = relationship(back_populates='physicians')
    
    reviews: Mapped["Review"] = relationship(back_populates="physician")
    
@dataclass
class Review(db.Model, SerializerMixin):
    serialize_rules = ('-user.')
    
    id: int = Column(Integer, primary_key=True)
    physician_score: int = Column(Integer, nullable=False)
    comment_to_physician: str = Column(String(100), nullable=True)
    attribute1: int = Column(Integer, nullable=True)
    attribute2: int = Column(Integer, nullable=True)
    attribute3: int = Column(Integer, nullable=True)
    attribute4: int = Column(Integer, nullable=True)
    attribute5: int = Column(Integer, nullable=True)
    
    
    physician_id: int = Column(ForeignKey("physician.id"))
    physician: Mapped["Physician"] = relationship(back_populates="review")
    


@dataclass
class Insurance(db.Model, SerializerMixin):
    serialize_rules = ('-user.insurance', '-center.insurances')

    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(50), unique=True, nullable=False)

    users: Mapped[List['User']] = relationship(back_populates='insurance')
    covers: Mapped[List['Center']] = relationship(secondary=coverage_table, back_populates='insurances')
