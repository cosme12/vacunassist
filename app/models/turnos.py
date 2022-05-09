
from app.models import get_db_connection

def get_turnos():
    """
    Devuelve todos los turnos
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    turnos = cursor.execute("select * from turno;").fetchall()
    conn.close()
    return turnos

def get_turnos_from_usuario(id):
    """
    Devuelve todos los turnos del usuario con id=id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    turnos = cursor.execute("select * from turno where id_usuario =? and estado =?;", (id,1,)).fetchall()
    conn.close()
    return turnos