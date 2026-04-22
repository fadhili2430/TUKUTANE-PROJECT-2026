from app import start_app, db
from app.utils import populate_initial_data

app = start_app() # call the function creating our app instance

with app.app_context():
    """do the database creation and data initialization within an app context (our running 'app')"""
    db.create_all()
    populate_initial_data()

if __name__ == "__main__":
    app.run(debug=True) # TODO: host, port may be later included and debug flag removed
