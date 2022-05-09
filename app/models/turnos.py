import hashlib
import random
import sqlite3
import string
from app.models import get_db_connection

def get_turnos():
    """
    Devuelve todos los turnos
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    turnos = cursor.execute("select * from turno").fetchall()
    conn.close()
    return turnos