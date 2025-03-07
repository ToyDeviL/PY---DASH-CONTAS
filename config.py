import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_really_strong_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://andrino:Rebecca%402023@localhost/contas'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
