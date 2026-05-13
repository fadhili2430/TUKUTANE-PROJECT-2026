from flask_login import UserMixin
from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, UTC
import secrets

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

user_activities = db.Table('user_activities',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('activity_id', db.Integer, db.ForeignKey('activity.id'), primary_key=True)
)

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

class CampusArea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    campus_area_id = db.Column(db.Integer, db.ForeignKey('campus_area.id'), nullable=False)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    campus_area = db.relationship('CampusArea', backref='users')
    activities = db.relationship('Activity', secondary=user_activities, backref=db.backref('users', lazy='dynamic'))
    events_organised = db.relationship('Event', backref='organiser', lazy=True)
    rsvps = db.relationship('RSVP', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        self.reset_token = secrets.token_urlsafe(32)
        from datetime import timedelta
        self.reset_token_expiry = datetime.now(UTC) + timedelta(hours=1)
        return self.reset_token

    def is_reset_token_valid(self, token):
        if not self.reset_token or self.reset_token != token:
            return False
        if not self.reset_token_expiry:
            return False
        expiry = self.reset_token_expiry
        if expiry.tzinfo is None:
            from datetime import timezone
            expiry = expiry.replace(tzinfo=timezone.utc)
        return datetime.now(UTC) < expiry

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    campus_area_id = db.Column(db.Integer, db.ForeignKey('campus_area.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    max_attendees = db.Column(db.Integer, nullable=False)
    organiser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    activity = db.relationship('Activity', backref='events')
    campus_area = db.relationship('CampusArea', backref='events')
    rsvps = db.relationship('RSVP', backref='event', lazy=True, cascade="all, delete-orphan")

    def is_full(self):
        return len([rsvp for rsvp in self.rsvps if rsvp.status == 'confirmed']) >= self.max_attendees

class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    status = db.Column(db.String(20), default='confirmed')
    timestamp = db.Column(db.DateTime, default=datetime.now(UTC))

    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='_user_event_uc'),)
