from app.models import get_db_connection

def get_vacunas_aplicadas(dni):
    """
    Devuelve las vacunas aplicadas de usuario
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    vacunas = cursor.execute("SELECT va.id , va.id_usuario, va.id_vacuna, fecha, lote, enfermedad, va.id_zona, laboratorio\
                            FROM usuario INNER JOIN vacuna_aplicada AS va ON usuario.id = va.id_usuario\
                            INNER JOIN vacuna ON va.id_vacuna = vacuna.id\
                            WHERE usuario.dni=?;", (dni,)).fetchall()
    conn.close
    return vacunas