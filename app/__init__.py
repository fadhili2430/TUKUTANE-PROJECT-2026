from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def start_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Register routes
    from app.routes import main
    app.register_blueprint(main)

    db.init_app(app)
    migrate.init_app(app, db)  
    
    return app
