import os

_db_url = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
if _db_url.startswith('postgres://'):
    _db_url = _db_url.replace('postgres://', 'postgresql://', 1)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tung-tung-tung-sahur'
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ENGINE_OPTIONS = (
        {'connect_args': {'timeout': 15}}
        if 'sqlite' in _db_url
        else {'pool_size': 10, 'pool_recycle': 3600, 'pool_pre_ping': True}
    )

    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Email (Gmail SMTP)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

    # App version for auto-update prompt
    APP_VERSION = '1.0.0'
