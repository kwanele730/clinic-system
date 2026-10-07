from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, Admin, Appointments, Patient, Nurse
from flask_cors import CORS
from datetime import datetime
import smtplib

from email.message import EmailMessage
import os
import re


app = Flask(__name__)

app.secret_key = "to_changed_later"

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///KwaDlangezwa-Clinic.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


with app.app_context():
    db.create_all()


# =========================================================
# VALIDATION FUNCTIONS
# =========================================================

def validate_email(email):
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return re.fullmatch(pattern, email) is not None


def validate_phone(phone):
    pattern = r'^0[6-8][0-9]{8}$'
    return re.fullmatch(pattern, phone) is not None


def validate_name(name):
    return name.replace(" ", "").isalpha()

def is_string(value):
    pattern = r"^[A-Za-z]+$"
    return bool(re.fullmatch(pattern, value))


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# ADMIN SIGN IN PAGE
# =========================================================

@app.route("/signin")
def signin():
    return render_template("SignIn.html")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("signin"))

    appointments = Appointments.query.all()

    return render_template(
        "dashboard.html",
        appointments=appointments
    )

@app.route("/nursedashboard")
def nurse_dash():
    appointments=Appointments.query.all()
    return render_template("nurse_view_appo.html", appointments=appointments)


# =========================================================
# ADD ADMIN PAGE
# =========================================================

@app.route("/addAdmin")
def addAdmin():
    return render_template("add_admin.html")


# =========================================================
# ADMINISTRATORS
# =========================================================

@app.route("/Admin")
def Admins():

    if "user_id" not in session:
        return redirect(url_for("signin"))

    administrators = Admin.query.all()

    return render_template(
        "administrators.html",
        administrators=administrators
    )


# =========================================================
# PATIENTS
# =========================================================

@app.route("/patients")
def patients():

    if "user_id" not in session:
        return redirect(url_for("signin"))

    patients = Patient.query.all()

    return render_template(
        "patients.html",
        patients=patients
    )


# =========================================================
# NURSES
# =========================================================

@app.route("/nurse")
def nurses():

    if "user_id" not in session:
        return redirect(url_for("signin"))

    nurses = Nurse.query.all()

    return render_template(
        "nurses.html",
        nurses=nurses
    )


@app.route("/nurse_view_details/<int:appointment_id>")
def nurse_view_details(appointment_id):

    appointment = Appointments.query.get_or_404(appointment_id)

    return render_template(
        "nurse_view_details.html",
        appointment=appointment
    )


# =========================================================
# BOOK APPOINTMENT PAGE
# =========================================================

@app.route("/booking")
def book():
    return render_template("book_appointment.html")


# =========================================================
# SETTINGS
# =========================================================

@app.route("/settings")
def settings():
    return render_template("setting.html")


# =========================================================
# REPORT
# =========================================================

@app.route("/generate")
def generate_report():
    return render_template("generate_report.html")


# =========================================================
# ADD NURSE PAGE
# =========================================================

@app.route("/add_nurse")
def eaddNurse():
    return render_template("add_nurse.html")


# =========================================================
# EDIT ADMIN DETAILS
# =========================================================

@app.route("/edit_admin/<int:admin_id>", methods=["POST", "GET"])
def editAdmin(admin_id):

    admin = Admin.query.get_or_404(
            admin_id
        )
    
    if request.method == "POST":

        name = request.form.get("name", "").strip()
        surname = request.form.get("surname", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone_no = request.form.get("phone_no", "").strip()
        

        if not all([
            name,
            surname,
            email,
            phone_no,
     
        ]):
            flash("Please complete all fields.", "danger")

            return redirect(
                url_for(
                    "editAdmin",
                    admin_id=admin.id
                )
            )

        if not is_string(name):
            flash(
                "Please enter a valid name.",
                "danger"
            )

            return redirect(
                url_for(
                    "editAdmin",
                    admin_id=admin.id
                )
            )

        if not is_string(surname):
            flash(
                "Please enter a valid surname.",
                "danger"
            )

            return redirect(
                url_for(
                    "editAdmin",
                    admin_id=admin.id
                )
            )

        if not validate_email(email):
            flash(
                "Please enter a valid email address.",
                "danger"
            )

            return redirect(
                url_for(
                    "editAdmin",
                    admin_id=admin.id
                )
            )

        if not validate_phone(phone_no):
            flash(
                "Please enter a valid cellphone number.",
                "danger"
            )

            return redirect(
                url_for(
                    "editAdmin",
                    admin_id=admin.id
                )
            )

        admin.name = name
        admin.surname = surname
        admin.email = email
        admin.phone_no = phone_no
       

        db.session.commit()

        flash(
            "admin updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "Admins",
                admin_id=admin.id
            )
        )

    return render_template(
        "edit_admin.html",
        admin=admin
    )


# =========================================================
# CREATE APPOINTMENT FROM ADMIN
# =========================================================

@app.route("/action_booking", methods=["POST"])
def action_book():

    name = request.form.get("name", "").strip()
    surname = request.form.get("surname", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone_no = request.form.get("phone_no", "").strip()
    reason = request.form.get("reason", "").strip()

    if not name or not surname or not email or not phone_no or not reason:
        flash("Please complete all fields.", "danger")
        return redirect(url_for("book"))

    if not validate_email(email):
        flash("Please enter a valid email address.", "danger")
        return redirect(url_for("book"))

    if not validate_phone(phone_no):
        flash("Please enter a valid cellphone number.", "danger")
        return redirect(url_for("book"))

    appointment = Appointments(
        name=name,
        surname=surname,
        email=email,
        phone_no=phone_no,
        reason=reason
    )

    db.session.add(appointment)
    db.session.commit()

    flash("Appointment successfully created.", "success")

    return redirect(url_for("dashboard"))


# =========================================================
# ADD NURSE
# =========================================================

@app.route("/add_nurse_details", methods=["POST"])
def add_nurse_details():

    name = request.form.get("name", "").strip()
    surname = request.form.get("surname", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone_no = request.form.get("phone_no", "").strip()
    password = request.form.get("password", "")

    if not all([name, surname, email, phone_no, password]):
        flash("Please complete all fields.", "danger")
        return redirect(url_for("eaddNurse"))

    if not validate_email(email):
        flash("Please enter a valid email address.", "danger")
        return redirect(url_for("eaddNurse"))

    if not validate_phone(phone_no):
        flash("Please enter a valid cellphone number.", "danger")
        return redirect(url_for("eaddNurse"))

    existing_nurse = Nurse.query.filter_by(email=email).first()

    if existing_nurse:
        flash("A nurse with this email already exists.", "danger")
        return redirect(url_for("eaddNurse"))

    nurse = Nurse(
        name=name,
        surname=surname,
        email=email,
        phone_no=phone_no,
        password=generate_password_hash(password)
    )

    db.session.add(nurse)
    db.session.commit()

    flash("Nurse successfully added.", "success")

    return redirect(url_for("nurses"))


# =========================================================
# DELETE NURSE
# =========================================================

@app.route("/delete_nurse/<int:nurse_id>", methods=["POST"])
def delete_nurse(nurse_id):

    if request.method=="POST":

        nurse = Nurse.query.get_or_404(nurse_id)

        db.session.delete(nurse)
        db.session.commit()

        flash("Nurse deleted successfully.", "success")

        return redirect(url_for("nurses"))
    return render_template('nurse.html')


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route("/signIn", methods=["POST"])
def SignIn():

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        flash("Email and password are required.", "danger")
        return redirect(url_for("signin"))

    if not validate_email(email):
        flash("Please enter a valid email address.", "danger")
        return redirect(url_for("signin"))

    user = Admin.query.filter_by(email=email).first()
    nurse = Nurse.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):

        session.clear()

        session["user_id"] = user.id
        session["name"] = user.name
        session["email"] = user.email
        session["role"] = "admin"
        session["logged_in"] = True

        return redirect(url_for("dashboard"))

    if nurse and check_password_hash(nurse.password, password):
    
        session.clear()

        session["nurse_id"] = nurse.id
        session["name"] = nurse.name
        session["email"] = nurse.email
        session["role"] = "admin"
        session["logged_in"] = True

        appointments=Appointments.query.all()

        return redirect(url_for("nurse_dash", appointments=appointments))

    flash("Invalid email or password.", "danger")

    return redirect(url_for("signin"))


# =========================================================
# ADD CLINIC ADMIN
# =========================================================

@app.route("/addClinicAdmin", methods=["POST"])
def addAdminDetails():

    name = request.form.get("name", "").strip()
    surname = request.form.get("surname", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    phone_no = request.form.get("phone_no", "").strip()

    if not all([name, surname, email, password, phone_no]):
        flash("Please complete all fields.", "danger")
        return redirect(url_for("addAdmin"))

    if not is_string(name):
        flash(
            "Please enter a valid name.",
            "danger"
        )

        return redirect(
            url_for(
                "addAdmin",
            )
        )

    if not is_string(surname):
        flash(
            "Please enter a valid surname.",
            "danger"
        )

        return redirect(
            url_for(
                "addAdmin",
            )
        )

    if not validate_email(email):
        flash("Please enter a valid email address.", "danger")
        return redirect(url_for("addAdmin"))

    if not validate_phone(phone_no):
        flash("Please enter a valid cellphone number.", "danger")
        return redirect(url_for("addAdmin"))

    existing_admin = Admin.query.filter_by(email=email).first()

    if existing_admin:
        flash("An administrator with this email already exists.", "danger")
        return redirect(url_for("addAdmin"))

    admin = Admin(
        name=name,
        surname=surname,
        email=email,
        password=generate_password_hash(password),
        phone_no=phone_no
    )

    db.session.add(admin)
    db.session.commit()

    flash("Successfully added.", "success")

    return redirect(url_for("dashboard"))


# =========================================================
# ADD CLINIC ADMIN
# =========================================================

@app.route("/addPatient", methods=["POST", "GET"])
def add_patient():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        surname = request.form.get("surname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone_no = request.form.get("phone_no", "").strip()

        if not all([name, surname, email, password, phone_no]):
            flash("Please complete all fields.", "danger")
            return redirect(url_for("add_patient"))

        if not is_string(name):
            flash(
                "Please enter a valid name.",
                "danger"
            )

            return redirect(
                url_for(
                    "add_patient",
                )
            )

        if not is_string(surname):
            flash(
                "Please enter a valid surname.",
                "danger"
            )

            return redirect(
                url_for(
                    "add_patient",
                )
            )

        if not validate_email(email):
            flash("Please enter a valid email address.", "danger")
            return redirect(url_for("add_patient"))

        if not validate_phone(phone_no):
            flash("Please enter a valid cellphone number.", "danger")
            return redirect(url_for("add_patient"))

        existing_Patient = Patient.query.filter_by(email=email).first()

        if existing_Patient:
            flash("An administrator with this email already exists.", "danger")
            return redirect(url_for("add_patient"))

        patient = Patient(
            name=name,
            surname=surname,
            email=email,
            password=generate_password_hash(password),
            phone_no=phone_no
        )

        db.session.add(patient)
        db.session.commit()

        flash("Successfully added.", "success")

        return redirect(url_for("patients"))
    return render_template('add_patient.html')



# =========================================================
# APPOINTMENT DETAILS
# =========================================================

@app.route("/appointment/<int:appointment_id>")
def appointment_details(appointment_id):

    appointment = Appointments.query.get_or_404(appointment_id)

    return render_template(
        "view.html",
        appointment=appointment
    )


# =========================================================
# SEND PATIENT NOTIFICATION
# =========================================================

@app.route(
    "/appointment/<int:appointment_id>/notify",
    methods=["POST"]
)
def send_patient_notification(appointment_id):

    appointment = Appointments.query.get_or_404(
        appointment_id
    )

    message = request.form.get("message", "").strip()

    flash(
        "Notification sent successfully.",
        "success"
    )

    return redirect(
        url_for(
            "appointment_details",
            appointment_id=appointment.id
        )
    )


@app.route(
    "/appointment/<int:appointment_id>/status",
    methods=["POST"]
)
def update_appointment_status(appointment_id):

    appointment = Appointments.query.get_or_404(
        appointment_id
    )

    new_status = request.form.get("status")

    if new_status not in [
        "Pending",
        "Confirmed",
        'inprogress',
        'assessed',
        "Cancelled",
        "Declined",
        "Rescheduled"
    ]:
        flash("Invalid appointment status.", "danger")
        return redirect(url_for("dashboard"))

    appointment.status = new_status

    db.session.commit()

    flash(
        "Appointment status updated successfully.",
        "success"
    )

    return redirect(url_for("dashboard"))




# nurse update Appointments


@app.route(
    "/nurse_appointment/<int:appointment_id>/status",
    methods=["POST"]
)
def nurse_update_appointment_status(appointment_id):

    appointment = Appointments.query.get_or_404(
        appointment_id
    )

    new_status = request.form.get("status")

    if new_status not in [
        "Pending",
        "Confirmed",
        'inprogress',
        'assessed',
        "Cancelled",
        "Declined",
        "Rescheduled"
    ]:
        flash("Invalid appointment status.", "danger")
        return redirect(url_for("nurse_dash"))

    appointment.status = new_status

    db.session.commit()

    flash(
        "Appointment status updated successfully.",
        "success"
    )

    return redirect(url_for("nurse_dash"))


# =========================================================
# DELETE APPOINTMENT
# =========================================================

@app.route(
    "/delete-appointment/<int:appointment_id>",
    methods=["POST"]
)
def delete_appointment(appointment_id):

    appointment = Appointments.query.get_or_404(
        appointment_id
    )

    db.session.delete(appointment)
    db.session.commit()

    flash(
        "Appointment deleted successfully.",
        "success"
    )

    return redirect(url_for("dashboard"))


# =========================================================
# NURSE DELETE APPOINTMENT
# =========================================================

@app.route(
    "/nurse_delete-appointment/<int:appointment_id>",
    methods=["POST"]
)
def nurse_delete_appointment(appointment_id):

    appointment = Appointments.query.get_or_404(
        appointment_id
    )

    db.session.delete(appointment)
    db.session.commit()

    flash(
        "Appointment deleted successfully.",
        "success"
    )

    return redirect(url_for("nurse_dash"))


# =========================================================
# DELETE PATIENT
# =========================================================

@app.route(
    "/delete-patient/<int:patient_id>",
    methods=["POST"]
)
def delete_patient(patient_id):

    patient = Patient.query.get_or_404(
        patient_id
    )

    db.session.delete(patient)
    db.session.commit()

    flash(
        "patient deleted successfully.",
        "success"
    )

    return redirect(url_for("patients"))


# =========================================================
# EDIT APPOINTMENT
# =========================================================

@app.route(
    "/editappointments/<int:appointment_id>",
    methods=["GET", "POST"]
)
def edit_appointment(appointment_id):

    appointment = Appointments.query.get_or_404(
        appointment_id
    )

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        surname = request.form.get("surname", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone_no = request.form.get("phone_no", "").strip()
        reason = request.form.get("reason", "").strip()

        if not all([
            name,
            surname,
            email,
            phone_no,
            reason
        ]):
            flash("Please complete all fields.", "danger")

            return redirect(
                url_for(
                    "edit_appointment",
                    appointment_id=appointment.id
                )
            )

        if not validate_email(email):
            flash(
                "Please enter a valid email address.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_appointment",
                    appointment_id=appointment.id
                )
            )

        if not validate_phone(phone_no):
            flash(
                "Please enter a valid cellphone number.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_appointment",
                    appointment_id=appointment.id
                )
            )

        appointment.name = name
        appointment.surname = surname
        appointment.email = email
        appointment.phone_no = phone_no
        appointment.reason = reason

        db.session.commit()

        flash(
            "Appointment updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "edit_appointment",
                appointment_id=appointment.id
            )
        )

    return render_template(
        "edit.html",
        appointment=appointment
    )


# =========================================================
# EDIT PATIENT
# =========================================================


@app.route(
    "/patients_details/<int:patient_id>",
    methods=["GET", "POST"]
)
def edit_patient(patient_id):

    patient = Patient.query.get_or_404(
        patient_id
    )

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        surname = request.form.get("surname", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone_no = request.form.get("phone_no", "").strip()
     

        if not all([
            name,
            surname,
            email,
            phone_no,
  
        ]):
            flash("Please complete all fields.", "danger")

            return redirect(
                url_for(
                    "edit_patient",
                    patient_id=patient.id
                )
            )

        if not is_string(name):
            flash(
                "Please enter a valid name",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_patient",
                    patient_id=patient.id
                )
            )

        if not is_string(surname):
            flash(
                "Please enter a valid surname.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_patient",
                    patient_id=patient.id
                )
            )

        if not validate_email(email):
            flash(
                "Please enter a valid email address.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_patient",
                    patient_id=patient.id
                )
            )

        if not validate_phone(phone_no):
            flash(
                "Please enter a valid cellphone number.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_patient",
                    patient_id=patient.id
                )
            )

        patient.name = name
        patient.surname = surname
        patient.email = email
        patient.phone_no = phone_no

        db.session.commit()

        flash(
            "patient updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "edit_patient",
                patient_id=patient.id
            )
        )

    return render_template(
        "edit_patient.html",
        patient=patient
    )

# =========================================================
# PATIENT DASHBOARD
# =========================================================

@app.route("/patient_dashboard")
def patient_dashboard():

    if "user_id" not in session:
        return redirect(url_for("patientlogin"))

    if session.get("role") != "patient":
        return redirect(url_for("patientlogin"))

    return render_template("patient_dashboard.html")


# =========================================================
# PATIENT REGISTRATION API
# =========================================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "No registration data received"
        }), 400

    name = data.get("firstName", "").strip()
    surname = data.get("surname", "").strip()
    email = data.get("email", "").strip().lower()
    phone_no = data.get("cellphone", "").strip()
    password = data.get("password", "")

    # Required fields
    if not all([
        name,
        surname,
        email,
        phone_no,
        password
    ]):
        return jsonify({
            "message": "Please provide all required fields"
        }), 400

    # Name validation
    if not validate_name(name):
        return jsonify({
            "message": "Name must contain letters only"
        }), 400

    # Surname validation
    if not validate_name(surname):
        return jsonify({
            "message": "Surname must contain letters only"
        }), 400

    # Email validation
    if not validate_email(email):
        return jsonify({
            "message": "Please enter a valid email address"
        }), 400

    # Phone validation
    if not validate_phone(phone_no):
        return jsonify({
            "message": (
                "Please enter a valid 10-digit "
                "South African cellphone number"
            )
        }), 400

    # Password validation
    if len(password) < 8:
        return jsonify({
            "message": (
                "Password must contain at least "
                "8 characters"
            )
        }), 400

    # Check duplicate email
    existing_patient = Patient.query.filter_by(
        email=email
    ).first()

    if existing_patient:
        return jsonify({
            "message": (
                "An account with this email "
                "already exists"
            )
        }), 409

    # Check duplicate phone
    existing_phone = Patient.query.filter_by(
        phone_no=phone_no
    ).first()

    if existing_phone:
        return jsonify({
            "message": (
                "An account with this cellphone "
                "number already exists"
            )
        }), 409

    # Create patient
    patient = Patient(
        name=name,
        surname=surname,
        email=email,
        phone_no=phone_no,
        password=generate_password_hash(password)
    )

    db.session.add(patient)
    db.session.commit()

    return jsonify({
        "message": "Registration successful",
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "surname": patient.surname,
            "email": patient.email,
            "cellphone": patient.phone_no
        }
    }), 201


# =========================================================
# PATIENT LOGIN API
# =========================================================

@app.route("/api/login", methods=["POST"])
def api_login():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "No login data received"
        }), 400

    identifier = data.get(
        "identifier",
        ""
    ).strip()

    password = data.get(
        "password",
        ""
    )

    if not identifier or not password:
        return jsonify({
            "message": (
                "Email/cellphone and password "
                "are required"
            )
        }), 400

    # Normalize email
    if "@" in identifier:
        identifier = identifier.lower()

    # Find patient by email OR cellphone
    patient = Patient.query.filter(
        (Patient.email == identifier) |
        (Patient.phone_no == identifier)
    ).first()

    # Patient doesn't exist
    if not patient:
        return jsonify({
            "message": (
                "Invalid email/cellphone "
                "or password"
            )
        }), 401

    # Check password
    if not check_password_hash(
        patient.password,
        password
    ):
        return jsonify({
            "message": (
                "Invalid email/cellphone "
                "or password"
            )
        }), 401

    # Create session
    session.clear()

    session["user_id"] = patient.id
    session["name"] = patient.name
    session["email"] = patient.email
    session["role"] = patient.role
    session["logged_in"] = True

    return jsonify({
        "message": "Login successful",
        "patient": {
            "id": patient.id,
            "name": patient.name,
            "surname": patient.surname,
            "email": patient.email,
            "cellphone": patient.phone_no
        }
    }), 200


# =========================================================
# CREATE APPOINTMENT API
# =========================================================

@app.route("/appointments", methods=["POST"])
def create_appointment():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "No appointment data received."
        }), 400

    patient_id = data.get("patient_id")
    date = data.get("date")
    reason = data.get("reason")

    if not patient_id or not date:
        return jsonify({
            "success": False,
            "message": (
                "Patient ID and appointment "
                "date are required."
            )
        }), 400

    # Make sure patient exists
    patient = Patient.query.get(patient_id)

    if not patient:
        return jsonify({
            "success": False,
            "message": "Patient does not exist."
        }), 404

    try:

        appointment_date = datetime.fromisoformat(
            date.replace("Z", "+00:00")
        )

        appointment = Appointments(
            patient_id=patient.id,
            name=patient.name,
            surname=patient.surname,
            email=patient.email,
            phone_no=patient.phone_no,
            reason=reason or "General consultation",
            status="pending"
        )

        db.session.add(appointment)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Appointment booked successfully.",
            "appointment": {
                "id": appointment.id,
                "patient_id": appointment.patient_id,
                "reason": appointment.reason,
                "status": appointment.status
            }
        }), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Could not create appointment."
        }), 500

# @app.route("/appointments", methods=["POST"])
# def create_appointment():

#     data = request.get_json()

#     if not data:
#         return jsonify({
#             "success": False,
#             "message": "No appointment data received."
#         }), 400

#     patient_id = data.get("patient_id")
#     date = data.get("date")
#     reason = data.get("reason")

#     if not patient_id or not date:
#         return jsonify({
#             "success": False,
#             "message": "Patient ID and appointment date are required."
#         }), 400

#     patient = Patient.query.get(patient_id)

#     if not patient:
#         return jsonify({
#             "success": False,
#             "message": "Patient does not exist."
#         }), 404

#     try:

#         appointment_date = datetime.fromisoformat(
#             date.replace("Z", "+00:00")
#         )

#         appointment = Appointments(
#             patient_id=patient.id,
#             reason=reason or "General consultation",
#             status="Confirmed"
#         )

#         db.session.add(appointment)
#         db.session.commit()

#         return jsonify({
#             "success": True,
#             "message": "Appointment booked successfully.",

#             "appointment": {
#                 "id": appointment.id,
#                 "patient_id": appointment.patient_id,

#                 "name": appointment.patient.name,
#                 "surname": appointment.patient.surname,
#                 "email": appointment.patient.email,
#                 "phone_no": appointment.patient.phone_no,

#                 "reason": appointment.reason,
#                 "status": appointment.status
#             }
#         }), 201

#     except Exception as e:

#         db.session.rollback()

#         print(e)

#         return jsonify({
#             "success": False,
#             "message": "Could not create appointment."
#         }), 500


# =========================================================
# DELETE ADMIN
# =========================================================

@app.route(
    "/delete-admin/<int:admin_id>",
    methods=["POST"]
)
def delete_admin(admin_id):

    admin = Admin.query.get_or_404(
        admin_id
    )

    db.session.delete(admin)
    db.session.commit()

    flash(
        "admin deleted successfully.",
        "success"
    )

    return redirect(url_for("Admins"))

@app.route("/appointment/<int:appointment_id>/notify", methods=["POST"])
def send_patient_email(appointment_id):

    appointment = Appointments.query.get_or_404(appointment_id)

    # Get message from textarea
    message_text = request.form.get("message", "").strip()

    if not message_text:
        flash("Please enter a message before sending.", "danger")
        return redirect(
            url_for(
                "appointment_details",
                appointment_id=appointment.id
            )
        )

    try:
        sender_email = os.getenv("MAIL_USERNAME")
        sender_password = os.getenv("MAIL_PASSWORD")

        if not sender_email or not sender_password:
            flash("Email settings are not configured.", "danger")
            return redirect(
                url_for(
                    "appointment_details",
                    appointment_id=appointment.id
                )
            )

        email = EmailMessage()

        email["Subject"] = "KwaDlangezwa Clinic - Notification"
        email["From"] = sender_email
        email["To"] = appointment.email

        email.set_content(
            f"""
            Dear {appointment.name},

            You have received a notification from KwaDlangezwa Clinic.

            {message_text}

            Regards,
            KwaDlangezwa Clinic
            """
                    )

        # Connect to Gmail
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(email)

        flash(
            f"Notification successfully sent to {appointment.email}.",
            "success"
        )

    except Exception as e:
        print("EMAIL ERROR:", e)

        flash(
            "The notification could not be sent. Please try again.",
            "danger"
        )

    return redirect(
        url_for(
            "appointment_details",
            appointment_id=appointment.id
        )
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("signin"))


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(
        debug=True,
        port=8080
    )