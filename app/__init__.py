from flask import Flask
from flask_bootstrap import Bootstrap5


class Config():
    TESTING = True
    DEBUG = True
    DATABASE = 'app/pruebadb'
    SECRET_KEY = 'password-super-dificil'
    WTF_CSRF_ENABLED = False,
    BOOTSTRAP_BTN_STYLE = 'success'


app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config.from_object(Config())

from app import routes

