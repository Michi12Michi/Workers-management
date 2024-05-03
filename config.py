from os import path

basedir = path.abspath(path.dirname(__file__))

class Config:
    DEBUG = True
    SECRET_KEY = "mylittlesecret"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + path.join(basedir, "data.sqlite")
