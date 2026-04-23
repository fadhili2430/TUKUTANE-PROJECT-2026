from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Event, RSVP, Activity, CampusArea
from .forms import SignupForm, LoginForm, EventForm, ProfileForm
from app import db

main = Blueprint('main', __name__)


@main.route("/")
def home():
    return render_template("home.html")


# =========================
# SIGNUP
# =========================

@main.route("/signup", methods=["GET", "POST"])
def signup():

    form = SignupForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:

            flash("Email already registered!")

            return redirect(
                url_for("main.login")
            )

        user = User(

            name=form.name.data,
            email=form.email.data,
            campus_area_id=form.campus_area.data

        )

        user.set_password(
            form.password.data
        )

        activity = Activity.query.get(
            form.activities.data
        )

        user.activities.append(
            activity
        )

        db.session.add(user)

        db.session.commit()

        login_user(user)

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "signup.html",
        form=form
    )


# =========================
# LOGIN
# =========================

@main.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and user.check_password(
            form.password.data
        ):

            login_user(user)

            return redirect(
                url_for("main.dashboard")
            )

        flash("Invalid credentials.")

    return render_template(
        "login.html",
        form=form
    )


# =========================
# DASHBOARD WITH SEARCH
# =========================

@main.route("/dashboard")
@login_required
def dashboard():

    activity_id = request.args.get(
        'activity'
    )

    campus_area_id = request.args.get(
        'campus_area'
    )

    search = request.args.get(
        'search'
    )

    query = Event.query

    if activity_id:

        query = query.filter_by(
            activity_id=activity_id
        )

    if campus_area_id:

        query = query.filter_by(
            campus_area_id=campus_area_id
        )

    if search:

        query = query.filter(
            Event.title.ilike(
                f"%{search}%"
            )
        )

    events = query.all()

    activities = Activity.query.all()

    campus_areas = CampusArea.query.all()

    return render_template(

        "dashboard.html",

        events=events,

        activities=activities,

        campus_areas=campus_areas

    )


# =========================
# CREATE EVENT
# =========================

@main.route("/event/new", methods=["GET", "POST"])
@login_required
def create_event():

    form = EventForm()

    if form.validate_on_submit():

        new_event = Event(

            title=form.title.data,

            description=form.description.data,

            activity_id=form.activity.data,

            campus_area_id=form.campus_area.data,

            date=form.date.data,

            time=form.time.data,

            max_attendees=form.max_attendees.data,

            organiser_id=current_user.id

        )

        db.session.add(new_event)

        db.session.commit()

        flash("Event created!")

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "create_event.html",
        form=form
    )


# =========================
# RSVP
# =========================

@main.route("/rsvp/<int:event_id>")
@login_required
def rsvp(event_id):

    event = Event.query.get_or_404(
        event_id
    )

    existing_rsvp = RSVP.query.filter_by(

        user_id=current_user.id,

        event_id=event_id

    ).first()

    if event.is_full():

        flash("Event is full!")

    elif existing_rsvp:

        if existing_rsvp.status == "cancelled":

            existing_rsvp.status = "confirmed"

            db.session.commit()

            flash("RSVP restored!")

        else:

            flash("Already RSVP'd!")

    else:

        new_rsvp = RSVP(

            user_id=current_user.id,

            event_id=event_id

        )

        db.session.add(new_rsvp)

        db.session.commit()

        flash(

            f"RSVP successful! "
            f"{event.remaining_slots()} slots left."

        )

    return redirect(
        url_for("main.dashboard")
    )


# =========================
# CANCEL RSVP
# =========================

@main.route("/cancel_rsvp/<int:event_id>")
@login_required
def cancel_rsvp(event_id):

    rsvp = RSVP.query.filter_by(

        user_id=current_user.id,

        event_id=event_id

    ).first()

    if rsvp:

        rsvp.status = "cancelled"

        db.session.commit()

        flash("RSVP cancelled!")

    return redirect(
        url_for("main.dashboard")
    )


# =========================
# ORGANIZER DASHBOARD
# =========================

@main.route("/organizer")
@login_required
def organizer():

    events = Event.query.filter_by(

        organiser_id=current_user.id

    ).all()

    return render_template(
        "organizer.html",
        events=events
    )


# =========================
# LOGOUT
# =========================

@main.route("/logout")
def logout():

    logout_user()

    return redirect(
        url_for("main.home")
    )