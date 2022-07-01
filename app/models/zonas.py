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


def asignar_zona(id_enfermero, id_zona):
    """
    Asigna una zona a un enfermero
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuario SET id_zona = ? WHERE id = ?;", (id_zona, id_enfermero))
    conn.commit()
    conn.close()


def set_direccion(id_zona, direccion):
    """
    Modifica la direccion de una zona
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE zona SET direccion = ? WHERE id = ?;", (direccion, id_zona))
    conn.commit()
    conn.close()

