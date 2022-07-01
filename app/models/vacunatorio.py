from app.models import get_db_connection


def get_telefono():
    """
    Devuelve el telefono
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    telefono = cursor.execute("SELECT * FROM vacunatorio where id =?;",(1,)).fetchone()
    conn.close
    return telefono


def set_telefono(telefono):
    """
    Modifica el telefono
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE vacunatorio SET telefono = ? WHERE id = ?;", (telefono, 1))
    conn.commit()
    conn.close()

