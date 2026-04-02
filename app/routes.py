from flask import Blueprint, render_template

main = Blueprint('main', __name__) # same functionality/properties as the main 'app' instance

@main.route("/")
def home():
	return render_template("home.html") # render some html
