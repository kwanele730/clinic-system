from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Admin(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    surname = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), nullable=False, unique=True)

    password = db.Column(db.String(100), nullable=False)

    phone_no = db.Column(db.String(100), nullable=False)

    role = db.Column(db.String(100), default="admin")

    date_created = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Patient(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    surname = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    phone_no = db.Column(
        db.String(10),
        nullable=False,
        unique=True
    )

    role = db.Column(
        db.String(20),
        default="patient"
    )

    date_created = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    


class Nurse(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    surname = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(100), nullable=False, unique=True)

    password = db.Column(db.String(100), nullable=False)

    phone_no = db.Column(db.String(100), nullable=False)

    role = db.Column(db.String(100), default="nurse")

    date_created = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Appointments(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Foreign key to Patient
    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patient.id"),
        nullable=True
    )

    name = db.Column(
        db.String(100),
        nullable=True
    )

    surname = db.Column(
        db.String(100),
        nullable=True
    )

    email = db.Column(
        db.String(100),
        nullable=True
    )

    phone_no = db.Column(
        db.String(100),
        nullable=True
    )

    reason = db.Column(
        db.String(100),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="Pending",
        nullable=True
    )

    date_created = db.Column(
        db.DateTime,
        default=datetime.utcnow

    )

    # Relationship with Patient
    patient = db.relationship(
        "Patient",
        backref="appointments"

    )

