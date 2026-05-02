from app import start_app, db
from app.utils import populate_initial_data

app = start_app()

with app.app_context():
    db.create_all()
    populate_initial_data()
