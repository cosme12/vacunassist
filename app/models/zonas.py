from app.models import get_db_connection


def get_zona(id):
    """
    Devuelve la zona con id=id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    zona = cursor.execute("SELECT * FROM zona where id =?;",(id,)).fetchone()
    conn.close
    return zona


def get_nombre_zona(id):
    """
    Devuelve el nombre de la zona con id=id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    zona = cursor.execute("SELECT nombre FROM zona where id =?;",(id,)).fetchone()
    conn.close
    return zona