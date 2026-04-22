from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

db = SQLAlchemy() # if we later scale up, replace simple sqlalchemy with mysql 'I guess'
migrate = Migrate()
login_manager = LoginManager()

def start_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__, 
                template_folder=os.path.join(basedir, '../templates'), 
                static_folder=os.path.join(basedir, '../static')) # handle a variety of user machines
    
    app.config['SECRET_KEY'] = 'tung-tung-tung-sahur' # flask-login session cookies uses this TODO: remove this
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # DB initialization
    db.init_app(app)
    migrate.init_app(app, db)  

    # Login Manager
    login_manager.init_app(app)
    login_manager.login_view = 'main.login' # send users here if not logged in

    # Register routes
    from app.routes import main
    app.register_blueprint(main)
    
    return app