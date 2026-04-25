import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tung-tung-tung-sahur'  # TODO: remove this
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False