from flask import Blueprint, render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Event, RSVP, Activity, CampusArea
from .forms import SignupForm, LoginForm, EventForm, ProfileForm, ForgotPasswordForm, ResetPasswordForm
from app import db, mail, MAIL_ENABLED
from datetime import datetime

try:
    from flask_mail import Message
except ImportError:
    Message = None
import logging
import os
import hmac
import hashlib
import subprocess
import sys

logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

# ─── Firebase Admin SDK (lazy-init so app still boots without credentials) ───
_firebase_app = None

def _get_firebase():
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app
    sa_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT', '')
    if not sa_json:
        return None
    try:
        import firebase_admin
        from firebase_admin import credentials
        import json
        cred = credentials.Certificate(json.loads(sa_json))
        _firebase_app = firebase_admin.initialize_app(cred)
        return _firebase_app
    except Exception as e:
        logger.error(f"Firebase init error: {e}")
        return None

def _send_push(fcm_token: str, title: str, body: str, url: str = ''):
    if not fcm_token:
        return
    try:
        _get_firebase()
        from firebase_admin import messaging
        msg = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data={'url': url} if url else {},
            token=fcm_token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    channel_id='tukutane_events',
                    sound='default',
                )
            )
        )
        messaging.send(msg)
        logger.info(f"Push notification sent to token ending ...{fcm_token[-6:]}")
    except Exception as e:
        logger.error(f"Push notification failed: {e}")

# ─── App version endpoint (used by Android for auto-update check) ────────────
APP_VERSION = '1.0.3'
APK_DOWNLOAD_URL = 'https://github.com/fadhili2430/TUKUTANE-PROJECT-2026/releases/latest'

@main.route('/api/version')
def app_version():
    return jsonify({'version': APP_VERSION, 'download_url': APK_DOWNLOAD_URL})

# ─── FCM token registration (called by Android app when user is logged in) ───
@main.route('/api/fcm-token', methods=['POST'])
@login_required
def register_fcm_token():
    token = request.form.get('token', '').strip()
    if not token:
        return jsonify({'error': 'missing token'}), 400
    try:
        current_user.fcm_token = token
        db.session.commit()
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"FCM token save error: {e}")
        return jsonify({'error': 'server error'}), 500

# ─── Auto-deploy webhook (called by GitHub on every push) ────────────────────
@main.route('/webhook/deploy', methods=['POST'])
def deploy_webhook():
    deploy_secret = os.environ.get('DEPLOY_SECRET', '')

    if deploy_secret:
        signature = request.headers.get('X-Hub-Signature-256', '')
        payload = request.get_data()
        expected = 'sha256=' + hmac.new(
            deploy_secret.encode(), payload, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            logger.warning("Deploy webhook: invalid signature")
            return jsonify({'error': 'Unauthorized'}), 401

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    python_exe = sys.executable
    results = {}

    try:
        r = subprocess.run(
            ['git', 'pull', 'origin', 'master'],
            cwd=project_root, capture_output=True, text=True, timeout=60
        )
        results['git_pull'] = r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        results['git_pull'] = f'error: {e}'

    try:
        req_file = os.path.join(project_root, 'requirements.txt')
        r = subprocess.run(
            [python_exe, '-m', 'pip', 'install', '-r', req_file, '-q'],
            cwd=project_root, capture_output=True, text=True, timeout=120
        )
        results['pip_install'] = 'ok' if r.returncode == 0 else r.stderr.strip()[:200]
    except Exception as e:
        results['pip_install'] = f'error: {e}'

    try:
        r = subprocess.run(
            [python_exe, '-m', 'flask', 'db', 'upgrade'],
            cwd=project_root, capture_output=True, text=True, timeout=60,
            env={**os.environ, 'FLASK_APP': 'wsgi.py'}
        )
        results['db_upgrade'] = 'ok' if r.returncode == 0 else r.stderr.strip()[:200]
    except Exception as e:
        results['db_upgrade'] = f'error: {e}'

    try:
        wsgi_path = os.path.join(project_root, 'wsgi.py')
        os.utime(wsgi_path, None)
        results['reload'] = 'wsgi.py touched — app will reload'
    except Exception as e:
        results['reload'] = f'error: {e}'

    logger.info(f"Deploy webhook completed: {results}")
    return jsonify({'status': 'deployed', 'details': results}), 200

# ─── Home ────────────────────────────────────────────────────────────────────
@main.route("/")
def home():
    return render_template("home.html")

# ─── Signup ──────────────────────────────────────────────────────────────────
@main.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            if User.query.filter_by(email=form.email.data).first():
                flash("Email already registered!")
                return redirect(url_for("main.login"))
            user = User(
                name=form.name.data,
                email=form.email.data,
                campus_area_id=form.campus_area.data
            )
            user.set_password(form.password.data)
            if form.activities.data:
                for activity_id in form.activities.data:
                    activity = Activity.query.get(activity_id)
                    if activity:
                        user.activities.append(activity)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for("main.dashboard"))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Signup error: {str(e)}")
            flash("An error occurred during signup. Please try again.")
    return render_template("signup.html", form=form)

# ─── Login ───────────────────────────────────────────────────────────────────
@main.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for("main.dashboard"))
            flash("Invalid credentials.")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash("An error occurred during login. Please try again.")
    return render_template("login.html", form=form)

# ─── Forgot Password ─────────────────────────────────────────────────────────
@main.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user:
            try:
                token = user.generate_reset_token()
                db.session.commit()
                if MAIL_ENABLED and mail and Message:
                    reset_url = url_for('main.reset_password', token=token, _external=True)
                    msg = Message(
                        subject="Tukutane — Reset Your Password",
                        recipients=[user.email],
                        html=render_template("email/reset_password.html", user=user, reset_url=reset_url)
                    )
                    mail.send(msg)
            except Exception as e:
                logger.error(f"Password reset email error: {str(e)}")
        flash("If that email is registered, a reset link has been sent. Check your inbox.")
        return redirect(url_for('main.login'))
    return render_template("forgot_password.html", form=form)

@main.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user or not user.is_reset_token_valid(token):
        flash("This reset link is invalid or has expired. Please request a new one.")
        return redirect(url_for('main.forgot_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            user.set_password(form.password.data)
            user.reset_token = None
            user.reset_token_expiry = None
            db.session.commit()
            flash("Password reset successfully! You can now log in.")
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Reset password error: {str(e)}")
            flash("An error occurred. Please try again.")
    return render_template("reset_password.html", form=form, token=token)

# ─── Dashboard ───────────────────────────────────────────────────────────────
@main.route("/dashboard")
@login_required
def dashboard():
    try:
        activity_id = request.args.get('activity')
        campus_area_id = request.args.get('campus_area')
        university = request.args.get('university')
        query = Event.query
        if activity_id:
            query = query.filter_by(activity_id=activity_id)
        if university:
            all_areas = CampusArea.query.all()
            matching_ids = [
                a.id for a in all_areas
                if a.name == university or a.name.lower().startswith(university.lower() + ' -')
            ]
            if matching_ids:
                query = query.filter(Event.campus_area_id.in_(matching_ids))
        elif campus_area_id:
            query = query.filter_by(campus_area_id=campus_area_id)
        events = query.all()
        activities = Activity.query.all()
        campus_areas = CampusArea.query.all()
        return render_template("dashboard.html", events=events, activities=activities, campus_areas=campus_areas)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash("An error occurred loading the dashboard. Please try again.")
        return redirect(url_for("main.home"))

# ─── Create Event ─────────────────────────────────────────────────────────────
@main.route("/event/new", methods=["GET", "POST"])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        try:
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
        except Exception as e:
            db.session.rollback()
            logger.error(f"Create event error: {str(e)}")
            flash("An error occurred creating the event. Please try again.")
    return render_template("create_event.html", form=form)

# ─── RSVP ────────────────────────────────────────────────────────────────────
@main.route("/rsvp/<int:event_id>")
@login_required
def rsvp(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        existing = RSVP.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        rsvp_confirmed = False
        if existing and existing.status == 'confirmed':
            flash("Already RSVP'd!")
        elif existing and existing.status == 'cancelled':
            if event.is_full():
                flash("Event is full!")
            else:
                existing.status = 'confirmed'
                db.session.commit()
                rsvp_confirmed = True
                flash("See you there!")
        else:
            if event.is_full():
                flash("Event is full!")
            else:
                new_rsvp = RSVP(user_id=current_user.id, event_id=event_id)
                db.session.add(new_rsvp)
                db.session.commit()
                rsvp_confirmed = True
                flash("See you there!")
        if rsvp_confirmed:
            _send_rsvp_notifications(event, current_user)
    except Exception as e:
        db.session.rollback()
        logger.error(f"RSVP error: {str(e)}")
        flash("An error occurred with your RSVP. Please try again.")
    return redirect(url_for("main.dashboard"))

def _send_rsvp_notifications(event, attendee):
    event_url = f"https://tukutaneproject.pythonanywhere.com/dashboard"

    # ── Email to attendee ──────────────────────────────────────────────────
    if MAIL_ENABLED and mail and Message:
        try:
            msg_attendee = Message(
                subject=f"Tukutane — You're going to {event.title}!",
                recipients=[attendee.email],
                html=render_template("email/rsvp_confirmation.html", event=event, user=attendee)
            )
            mail.send(msg_attendee)
        except Exception as e:
            logger.error(f"RSVP confirmation email failed: {e}")

    # ── Email + Push notification to organiser ─────────────────────────────
    try:
        organiser = User.query.get(event.organiser_id)
        if organiser and organiser.email != attendee.email:
            # Email
            if MAIL_ENABLED and mail and Message:
                try:
                    msg_organiser = Message(
                        subject=f"Tukutane — New RSVP for {event.title}",
                        recipients=[organiser.email],
                        html=render_template("email/rsvp_organiser_notify.html",
                                             event=event, attendee=attendee, organiser=organiser)
                    )
                    mail.send(msg_organiser)
                except Exception as e:
                    logger.error(f"RSVP organiser email failed: {e}")

            # Push notification (FCM)
            if organiser.fcm_token:
                _send_push(
                    fcm_token=organiser.fcm_token,
                    title=f"New RSVP — {event.title}",
                    body=f"{attendee.name} just joined your event!",
                    url=event_url
                )

        # ── Push notification to attendee too (confirmation) ───────────────
        if attendee.fcm_token:
            _send_push(
                fcm_token=attendee.fcm_token,
                title=f"You're going to {event.title}!",
                body=f"RSVP confirmed. See you there!",
                url=event_url
            )
    except Exception as e:
        logger.error(f"RSVP notification error: {e}")

# ─── Cancel RSVP ─────────────────────────────────────────────────────────────
@main.route("/cancel_rsvp/<int:event_id>")
@login_required
def cancel_rsvp(event_id):
    try:
        rsvp = RSVP.query.filter_by(user_id=current_user.id, event_id=event_id).first()
        if rsvp:
            rsvp.status = 'cancelled'
            db.session.commit()
            flash("RSVP cancelled!")
        else:
            flash("RSVP not found.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Cancel RSVP error: {str(e)}")
        flash("An error occurred cancelling your RSVP. Please try again.")
    return redirect(url_for("main.dashboard"))

# ─── RSVPs list ──────────────────────────────────────────────────────────────
@main.route("/rsvps")
@login_required
def rsvps():
    try:
        user_rsvps = RSVP.query.filter_by(user_id=current_user.id, status='confirmed').all()
        return render_template("rsvps.html", rsvps=user_rsvps)
    except Exception as e:
        logger.error(f"RSVPs view error: {str(e)}")
        flash("An error occurred loading your RSVPs. Please try again.")
        return redirect(url_for("main.dashboard"))

# ─── Profile ─────────────────────────────────────────────────────────────────
@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        try:
            current_user.name = form.name.data
            current_user.email = form.email.data
            current_user.campus_area_id = form.campus_area.data
            current_user.activities = []
            if form.activities.data:
                for activity_id in form.activities.data:
                    activity = Activity.query.get(activity_id)
                    if activity:
                        current_user.activities.append(activity)
            db.session.commit()
            flash("Profile updated!")
            return redirect(url_for("main.dashboard"))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Profile update error: {str(e)}")
            flash("An error occurred updating your profile. Please try again.")
    elif request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.campus_area.data = current_user.campus_area_id
        if current_user.activities:
            form.activities.data = [activity.id for activity in current_user.activities]
    return render_template("profile.html", form=form)

# ─── Organizer ───────────────────────────────────────────────────────────────
@main.route("/organizer")
@login_required
def organizer():
    try:
        events = Event.query.filter_by(organiser_id=current_user.id).all()
        return render_template("organizer.html", events=events)
    except Exception as e:
        logger.error(f"Organizer view error: {str(e)}")
        flash("An error occurred loading your events. Please try again.")
        return redirect(url_for("main.dashboard"))

@main.route('/organizer/dashboard', methods=['GET'])
@login_required
def organizer_dashboard():
    try:
        events = Event.query.filter_by(organiser_id=current_user.id).all()
        return render_template('organizer_dashboard.html', events=events)
    except Exception as e:
        logger.error(f"Organizer dashboard error: {str(e)}")
        flash("An error occurred loading the organizer dashboard. Please try again.")
        return redirect(url_for("main.dashboard"))

# ─── Edit Event ───────────────────────────────────────────────────────────────
@main.route("/event/edit/<int:event_id>", methods=["GET", "POST"])
@login_required
def edit_event(event_id):
    try:
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
        return render_template("edit_event.html", form=form, event=event)
    except Exception as e:
        logger.error(f"Edit event error: {str(e)}")
        flash("An error occurred editing the event. Please try again.")
        return redirect(url_for("main.organizer"))

# ─── Cancel Event ─────────────────────────────────────────────────────────────
@main.route("/event/cancel/<int:event_id>")
@login_required
def cancel_event(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        if event.organiser_id != current_user.id:
            flash("Unauthorized!")
            return redirect(url_for("main.dashboard"))
        db.session.delete(event)
        db.session.commit()
        flash("Event cancelled!")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Cancel event error: {str(e)}")
        flash("An error occurred cancelling the event. Please try again.")
    return redirect(url_for("main.organizer"))

# ─── View RSVPs ───────────────────────────────────────────────────────────────
@main.route("/event/<int:event_id>/rsvps")
@login_required
def view_rsvps(event_id):
    try:
        event = Event.query.get_or_404(event_id)
        if event.organiser_id != current_user.id:
            flash("Unauthorized!")
            return redirect(url_for("main.dashboard"))
        rsvps = RSVP.query.filter_by(event_id=event_id, status='confirmed').all()
        return render_template("view_rsvps.html", event=event, rsvps=rsvps)
    except Exception as e:
        logger.error(f"View RSVPs error: {str(e)}")
        flash("An error occurred viewing RSVPs. Please try again.")
        return redirect(url_for("main.dashboard"))

# ─── Logout ───────────────────────────────────────────────────────────────────
@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))
