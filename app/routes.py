from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Event
from app import db


main = Blueprint('main', __name__) # same functionality/properties as the main 'app' instance


@main.route("/")
def home():
	return render_template("home.html") # render some html


@main.route("/signup", methods=["GET", "POST"])
def signup():
	if request.method == "POST": # we will be using the method `POST` in conjunction with form tags at the frontend for security
		username = request.form['username']
		password = request.form['password']
		new_user = User(username=username)
		new_user.set_password(password)
		db.session.add(new_user)
		db.session.commit()
		login_user(new_user) # log users in as soon as they sign up
		flash("Account Created Successfully. Welcome onboard!")
		return redirect(url_for("main.dashboard"))
	return render_template("signup.html")


@main.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form['username']
		# email = request.form.get("email") # TODO: give user choice to choose between email and username for logging in
		password = request.form['password']
		user = User.query.filter_by(username=username).first()
		if user and user.check_password(password):
			login_user(user)
			flash("Logged in Successfully. Welcome back!")
			return redirect(url_for("main.dashboard"))

		else:
			flash("Invalid credentils. GET LOST!")
			return redirect(url_for("main.login"))

	return render_template("login.html")


@main.route("/dashboard", methods=["GET", "POST"])
def dashboard():
	#flash("Welcome")				# TODO: fix flash method 
	return render_template("dashboard.html")
# TODO: needs improvement

@main.route("/event/new", methods=["GET", "POST"])
def create_event():
    if request.method == "POST":
        new_event = Event(
            title=request.form['title'],
            description=request.form['description'],
            location=request.form['location'],
            capacity=int(request.form['capacity']),
            category=request.form['category'],
            organiser_id=1 # TODO: Change this to current_user.id after setting up Flask-Login
        )
        
        db.session.add(new_event)
        db.session.commit()
        
        flash("Event created successfully!")
        return redirect(url_for("main.dashboard"))
    
    return render_template("create_event.html")

@main.route("/logout", methods=["GET", "POST"])
def logout():
	logout_user() # end session
	flash("Logged out Successfully. Come back again!!")
	return redirect(url_for('main.home'))


@main.route("/signout", methods=["GET", "POST"]) # completely delete account
def signout():
	#flash("Signing out.. We are sad to see you leave!!")
	return redirect(url_for('main.home')) # TODO: safely delete entries from the database