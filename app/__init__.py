from flask import Flask
from flask_bootstrap import Bootstrap5


class Config():
    TESTING = True
    DEBUG = True
    DATABASE = 'app/pruebadb'
    #DATABASE = 'app/demo2'
    SECRET_KEY = 'password-super-dificil'
    WTF_CSRF_ENABLED = False,
    BOOTSTRAP_BTN_STYLE = 'success'
    EMAIL_ENABLED = False


app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config.from_object(Config())

from app import routes

