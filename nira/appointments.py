from datetime import date
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    flash,
    session,
)
import uuid
from nira import db
from nira.config import Config
from nira.models import Appointment

MOGADISHU_DISTRICTS = [
    "Abdiaziz",
    "Bondhere",
    "Dayniile",
    "Dharkenley",
    "Garasbaley",
    "Hamar Jajab",
    "Hamar Weyne",
    "Hawle Wadaag",
    "Hodan",
    "Kaaran",
    "Kahda",
    "Shangani",
    "Shibis",
    "Wadajir",
    "Waberi",
    "Wardhiigley",
    "Yaqshid",
    "Other",
]

appointments_bp = Blueprint("appointments", __name__)


def get_available_dates():
    today = date.today()
    return Appointment.availability(
        today,
        Config.BOOKING_WINDOW_DAYS,
        Config.DAILY_APPOINTMENT_LIMIT,
    )


def get_all_dates_with_remaining():
    today = date.today()
    return Appointment.availability(
        today,
        Config.BOOKING_WINDOW_DAYS,
        Config.DAILY_APPOINTMENT_LIMIT,
        include_full=True,
    )


@appointments_bp.route("/", methods=["GET", "POST"])
def landing():
    limit = Config.DAILY_APPOINTMENT_LIMIT
    available_dates = get_available_dates()
    full_window = get_all_dates_with_remaining()

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        mother_full_name = request.form.get("mother_full_name", "").strip()
        email = request.form.get("email", "").strip() or None
        phone = request.form.get("phone", "").strip()
        district = request.form.get("district", "").strip()
        dob_raw = request.form.get("date_of_birth", "").strip()
        national_id = request.form.get("national_id", "").strip() or None
        preferred_time = request.form.get("preferred_time", "").strip() or None
        visit_reason = request.form.get("visit_reason", "").strip() or None
        notes = request.form.get("notes", "").strip() or None
        visit_date_raw = request.form.get("visit_date")

        try:
            visit_date = date.fromisoformat(visit_date_raw)
        except Exception:
            visit_date = None

        try:
            date_of_birth = date.fromisoformat(dob_raw)
        except Exception:
            date_of_birth = None

        valid_dates = {d["date"] for d in available_dates}

        validation_errors = []
        if not full_name:
            validation_errors.append("Please add your full name so we can reserve your slot.")
        if not mother_full_name:
            validation_errors.append("Add your mother's full name for identification.")
        if not phone:
            validation_errors.append("Phone number is required so we can reach you.")
        if not district:
            validation_errors.append("District is required.")
        if not date_of_birth:
            validation_errors.append("Please provide your date of birth.")
        if not visit_reason:
            validation_errors.append("Tell us your purpose to personalize support.")
        if not visit_date or visit_date not in valid_dates:
            validation_errors.append("That date is not available anymore. Please pick another day.")

        if validation_errors:
            flash(validation_errors[0], "error")
        else:
            taken = Appointment.slots_taken(visit_date)
            if taken >= limit:
                flash("That day just filled up. Please choose another date.", "error")
            else:
                confirmation_code = uuid.uuid4().hex
                appointment = Appointment(
                    confirmation_code=confirmation_code,
                    full_name=full_name,
                    mother_full_name=mother_full_name,
                    email=email,
                    phone=phone,
                    district=district,
                    date_of_birth=date_of_birth,
                    national_id=national_id,
                    preferred_time=preferred_time,
                    visit_reason=visit_reason,
                    visit_date=visit_date,
                    notes=notes,
                )
                db.session.add(appointment)
                db.session.commit()
                return redirect(
                    url_for("appointments.print_appointment", code=confirmation_code)
                )

        # refresh availability in case a slot closed while posting
        available_dates = get_available_dates()

    availability_payload = [
        {"date": d["date"].isoformat(), "remaining": d["remaining"]}
        for d in available_dates
    ]

    return render_template(
        "appointment.html",
        available_dates=available_dates,
        daily_limit=limit,
        availability_payload=[
            {"date": d["date"].isoformat(), "remaining": d["remaining"]} for d in full_window
        ],
        districts=MOGADISHU_DISTRICTS,
    )


@appointments_bp.route("/availability")
def availability_api():
    data = [
        {"date": d["date"].isoformat(), "remaining": d["remaining"]}
        for d in get_available_dates()
    ]
    return jsonify(
        {"available_dates": data, "daily_limit": Config.DAILY_APPOINTMENT_LIMIT}
    )


def _admin_logged_in():
    return session.get("admin_logged_in") is True


@appointments_bp.before_app_request
def protect_admin_dashboard():
    protected = {"appointments.admin_appointments", "appointments.admin_appointments_by_date"}
    if request.endpoint in protected and not _admin_logged_in():
        return redirect(url_for("appointments.admin_login"))


@appointments_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if _admin_logged_in():
        return redirect(url_for("appointments.admin_appointments"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == "admin" and password == "admin@123":
            session.pop("_flashes", None)
            session["admin_logged_in"] = True
            flash("Welcome back, Admin.", "success")
            return redirect(url_for("appointments.admin_appointments"))
        else:
            flash("Invalid credentials. Try again.", "error")

    return render_template("admin_login.html")


@appointments_bp.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Logged out.", "success")
    return redirect(url_for("appointments.admin_login"))


@appointments_bp.route("/admin/appointments")
def admin_appointments():
    today = date.today()
    dates = (
        Appointment.query.with_entities(Appointment.visit_date, db.func.count(Appointment.id))
        .group_by(Appointment.visit_date)
        .order_by(Appointment.visit_date.asc())
        .all()
    )
    total = sum(count for _, count in dates)
    upcoming = sum(count for d, count in dates if d >= today)
    today_count = sum(count for d, count in dates if d == today)

    return render_template(
        "admin_dates.html",
        date_counts=dates,
        total=total,
        upcoming=upcoming,
        today=today_count,
        today_date=today,
        daily_limit=Config.DAILY_APPOINTMENT_LIMIT,
    )


@appointments_bp.route("/admin/appointments/<date_str>")
def admin_appointments_by_date(date_str):
    if not _admin_logged_in():
        return redirect(url_for("appointments.admin_login"))

    try:
        visit_date = date.fromisoformat(date_str)
    except Exception:
        flash("Invalid date.", "error")
        return redirect(url_for("appointments.admin_appointments"))

    appointments = (
        Appointment.query.filter_by(visit_date=visit_date)
        .order_by(Appointment.created_at.desc())
        .all()
    )

    return render_template(
        "admin_appointments.html",
        appointments=appointments,
        visit_date=visit_date,
    )


@appointments_bp.route("/appointment/<code>/print")
def print_appointment(code):
    appointment = Appointment.query.filter_by(confirmation_code=code).first_or_404()
    verify_url = url_for("appointments.verify_appointment", code=appointment.confirmation_code, _external=True)
    return render_template(
        "print_appointment.html",
        appointment=appointment,
        verify_url=verify_url,
    )


@appointments_bp.route("/verify")
def verify_appointment():
    code = request.args.get("code", "").strip()
    appointment = Appointment.query.filter_by(confirmation_code=code).first()
    return render_template(
        "verify.html",
        appointment=appointment,
        code=code,
    )
