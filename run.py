from app import start_app
from app.utils import populate_initial_data

app = start_app()

with app.app_context():
    populate_initial_data()

if __name__ == "__main__":
    app.run(debug=True)
