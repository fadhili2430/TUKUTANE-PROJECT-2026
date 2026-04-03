from flask import Blueprint, render_template, request, redirect, flash, url_for

main = Blueprint('main', __name__) # same functionality/properties as the main 'app' instance

@main.route("/")
def home():
	return render_template("home.html") # render some html

@main.route("/signup", methods=["GET", "POST"])
def signup():
	if request.method == "POST": # we will be using the method `POST` in conjunction with form tags at the frontend for security
		username = request.form.get("username")
		email = request.form.get("email")
		password = request.form.get("password") # data validation and sanitation can be done on the frontend unless stated otherwise
		confirm_pass = request.form.get("confirm_password")
		##university = request.form.get("university") #future improvement

		# TODO: integrate databases or persistent storage

		flash("Account Created Successfully. Welcome onboard!")
		return redirect(url_for("main.dashboard"))
	return render_template("signup.html")


@main.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		username = request.form.get("username")
		# email = request.form.get("email") # TODO: give user choice to choose between email and username for logging in
		password = request.form.get("password")

		# TODO: integrate databases or persistent storage

		flash("Logged in Successfully. Welcome back!")
		return redirect(url_for("main.dashboard"))
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
 




