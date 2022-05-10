from app.models import get_db_connection

def get_vacunas_aplicadas(dni):
    """
    Devuelve las vacunas aplicadas de usuario
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    vacunas = cursor.execute("SELECT * FROM usuario \
                            INNER JOIN vacuna_aplicada ON usuario.id = vacuna_aplicada.id_usuario\
                            INNER JOIN vacuna ON vacuna_aplicada.id_vacuna = vacuna.id \
                            WHERE usuario.dni = ?;" (dni,)).fetchall()
    conn.close
    return vacunas