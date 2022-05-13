import sqlite3
from app import app
from flask import current_app

DATABASE = app.config['DATABASE']


def get_db_connection():
    """
    Establece la conexion con la db
    """
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


from app.models.usuarios import *
from app.models.turnos import *
from app.models.vacunas import *
from app.models.vacunas_aplicadas import *
from app.models.zonas import *

