from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

try:
    from flask_mail import Mail
    mail = Mail()
    MAIL_ENABLED = True
except ImportError:
    mail = None
    MAIL_ENABLED = False

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def start_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    app = Flask(__name__,
                template_folder=os.path.join(basedir, '../templates'),
                static_folder=os.path.join(basedir, '../static'))

    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    if MAIL_ENABLED and mail is not None:
        mail.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app
