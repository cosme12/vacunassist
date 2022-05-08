import sqlite3

DATABASE = 'app/pruebadb'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


from app.models.usuarios import *

