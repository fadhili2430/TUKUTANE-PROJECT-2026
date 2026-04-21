from app import start_app, db
from app.utils import populate_initial_data
from app.models import Activity, CampusArea, User, Event, RSVP

app = start_app()

with app.app_context():
    db.create_all()
    populate_initial_data()

if __name__ == "__main__":
    app.run(debug=True)
