from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField, TimeField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange
from .models import Activity, CampusArea

class SignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    campus_area = SelectField('Campus Area', coerce=int, validators=[DataRequired()])
    activities = SelectField('Interests', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.campus_area.choices = [(area.id, area.name) for area in CampusArea.query.all()]
        self.activities.choices = [(activity.id, activity.name) for activity in Activity.query.all()]

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    activity = SelectField('Activity', coerce=int, validators=[DataRequired()])
    campus_area = SelectField('Campus Area', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    max_attendees = IntegerField('Max Attendees', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Create Event')

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.activity.choices = [(activity.id, activity.name) for activity in Activity.query.all()]
        self.campus_area.choices = [(area.id, area.name) for area in CampusArea.query.all()]

class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    campus_area = SelectField('Campus Area', coerce=int, validators=[DataRequired()])
    activities = SelectField('Interests', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Update Profile')

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.campus_area.choices = [(area.id, area.name) for area in CampusArea.query.all()]
        self.activities.choices = [(activity.id, activity.name) for activity in Activity.query.all()]