from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Event, RSVP, Activity, CampusArea
from .forms import SignupForm, LoginForm, EventForm, ProfileForm
from app import db
from datetime import datetime

main = Blueprint('main', __name__)

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered!")
            return redirect(url_for("main.signup"))
        
        user = User(
            name=form.name.data,
            email=form.email.data,
            campus_area_id=form.campus_area.data
        )
        user.set_password(form.password.data)
        activity = Activity.query.get(form.activities.data)
        user.activities.append(activity)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("main.dashboard"))
    return render_template("signup.html", form=form)

@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("main.dashboard"))
        flash("Invalid credentials.")
    return render_template("login.html", form=form)

@main.route("/dashboard")
@login_required
def dashboard():
    # Goal: Allow students to discover events [cite: 27, 34]
    events = Event.query.all()
    return render_template("dashboard.html", events=events)

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
        return redirect(url_for("main.dashboard"))
    return render_template("create_event.html", form=form)

@main.route("/rsvp/<int:event_id>")
@login_required
def rsvp(event_id):
    # Goal: RSVP system with capacity enforcement [cite: 35, 60]
    event = Event.query.get_or_404(event_id)
    if event.is_full():
        flash("Event is full!")
    elif RSVP.query.filter_by(user_id=current_user.id, event_id=event_id).first():
        flash("Already RSVP'd!")
    else:
        new_rsvp = RSVP(user_id=current_user.id, event_id=event_id)
        db.session.add(new_rsvp)
        db.session.commit()
        flash("See you there!")
    return redirect(url_for("main.dashboard"))

@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.campus_area_id = form.campus_area.data
        current_user.activities = [Activity.query.get(form.activities.data)]
        db.session.commit()
        flash("Profile updated!")
        return redirect(url_for("main.dashboard"))
    elif request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.campus_area.data = current_user.campus_area_id
        if current_user.activities:
            form.activities.data = current_user.activities[0].id
    return render_template("profile.html", form=form)


@main.route("/cancel_rsvp/<int:event_id>")
@login_required
def cancel_rsvp(event_id):
    rsvp = RSVP.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if rsvp:
        rsvp.status = 'cancelled'
        db.session.commit()
        flash("RSVP cancelled!")
    return redirect(url_for("main.dashboard"))

@main.route("/organizer")
@login_required
def organizer_dashboard():
    events = Event.query.filter_by(organiser_id=current_user.id).all()
    return render_template("organizer_dashboard.html", events=events)

@main.route("/event/edit/<int:event_id>", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organiser_id != current_user.id:
        flash("Unauthorized!")
        return redirect(url_for("main.dashboard"))
    form = EventForm()
    if form.validate_on_submit():
        event.title = form.title.data
        event.description = form.description.data
        event.activity_id = form.activity.data
        event.campus_area_id = form.campus_area.data
        event.date = form.date.data
        event.time = form.time.data
        event.max_attendees = form.max_attendees.data
        db.session.commit()
        flash("Event updated!")
        return redirect(url_for("main.organizer_dashboard"))
    elif request.method == "GET":
        form.title.data = event.title
        form.description.data = event.description
        form.activity.data = event.activity_id
        form.campus_area.data = event.campus_area_id
        form.date.data = event.date
        form.time.data = event.time
        form.max_attendees.data = event.max_attendees
    return render_template("edit_event.html", form=form)

@main.route("/event/cancel/<int:event_id>")
@login_required
def cancel_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organiser_id != current_user.id:
        flash("Unauthorized!")
        return redirect(url_for("main.dashboard"))
    db.session.delete(event)
    db.session.commit()
    flash("Event cancelled!")
    return redirect(url_for("main.organizer_dashboard"))

@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))

@main.route("/event/<int:event_id>/rsvps")
@login_required
def view_rsvps(event_id):
    event = Event.query.get_or_404(event_id)
    if event.organiser_id != current_user.id:
        flash("Unauthorized!")
        return redirect(url_for("main.dashboard"))
    rsvps = RSVP.query.filter_by(event_id=event_id, status='confirmed').all()
    return render_template("rsvps.html", event=event, rsvps=rsvps)
