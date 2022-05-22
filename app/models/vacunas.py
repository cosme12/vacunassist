from app.models import get_db_connection

def get_vacuna(id):
    """
    Devuelve la vacuna con id=id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    vacuna = cursor.execute("SELECT * FROM vacuna where id =?;",(id,)).fetchone()
    conn.close()
    return vacuna

def get_vacuna_aplicada(id):
    """
    Devuelve enfermedad, laboratorio, lote, fecha y zona de la vacuna apliacada con id=id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    vacuna = cursor.execute("SELECT id_zona, fecha, enfermedad, lote, laboratorio, zona.nombre AS zona\
                            FROM vacuna_aplicada AS va INNER JOIN vacuna ON va.id_vacuna=vacuna.id\
                            INNER JOIN zona ON id_zona=zona.id\
                            WHERE va.id =?;",(id,)).fetchone()
    conn.close()
    return vacuna

def get_id_vacuna(enfermedad):
    """
    Devuelve el id de la vacuna con enfermedad=enfermedad
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    vacuna = cursor.execute("SELECT id FROM vacuna WHERE enfermedad=?;",(enfermedad,)).fetchone()
    conn.close()
    return vacuna
