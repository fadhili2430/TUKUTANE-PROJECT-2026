from app import db

user_interests = db.Table('user_interests',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'), primary_key=True)
)

class User(db.Model):
    """Table for student Accounts and Profiles"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    #Relationships
    events_organised = db.relationship('Event', backref='organiser', lazy=True)
    interests = db.relationship('Interest', secondary=user_interests, backref=db.backref('users', lazy='dynamic'))
    rsvps = db.relationship('RSVP', backref='user', lazy=True)

    def __repr__(self):
         return f'<User {self.username}>'

class Event(db.Model):
    """Table for Campus Meetups and Social Activities"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    organiser_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    rsvps = db.relationship('RSVP', backref='event', lazy=True)

    def __repr__(self):
        return f'<Event {self.title}>'

class RSVP(db.Model):
    """Attendance and Capacity Control Logic"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    __table_args__= (db.UniqueConstraint('user_id', 'event_id', name='_user_event_uc'),)

    def __repr__(self):
        return f'<RSVP User:{self.user_id} Event:{self.event_id}>'

class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<Interest {self.name}>'