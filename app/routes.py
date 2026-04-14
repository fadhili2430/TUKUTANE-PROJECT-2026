from flask import Blueprint, render_template, request, redirect, flash, url_for
from .models import User
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
			flash("Logged in Successfully. Welcome back!")
			return redirect(url_for("main.dashboard"))

		else:
			flash("Invalid credentils. GET LOST!")
			return redirect(url_for("main.home"))

	return render_template("login.html")


@main.route("/dashboard", methods=["GET", "POST"])
def dashboard():
	#flash("Welcome")				# TODO: fix flash method 
	return render_template("dashboard.html")
# TODO: needs improvement


@main.route("/logout", methods=["GET", "POST"])
def logout():
	#flash("Logged out Successfully. Come back again!!")
	return render_template("logout.html")

@main.route("/signout", methods=["GET", "POST"])
def signout():
	#flash("Signing out.. We are sad to see you leave!!")
	return render_template("signout.html") # TODO: safely delete entries from the database