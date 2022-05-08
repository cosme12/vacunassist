from app.models import get_db_connection, make_dicts


def existe_usuario(nombre):
    """
    Devuelve True si el usuario existe en la base de datos
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select COUNT('nombre') from usuarios where nombre=?;", (nombre,))
    existe = cursor.fetchone()[0]
    conn.close()
    return existe


def get_usuarios():
    """
    Devuelve todos los usuarios
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    #usuarios = make_dicts(cursor, cursor.execute("select * from usuarios;"))
    usuarios = cursor.execute("select * from usuarios;").fetchall()
    conn.close()
    return usuarios