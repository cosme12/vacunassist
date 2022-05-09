from app.models import get_db_connection

def get_vacuna(id):
    """
    Devuelve la vacuna con id=id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    vacuna = cursor.execute("SELECT * FROM vacuna where id =?;",(id)).fetchone()
    conn.close
    return vacuna
