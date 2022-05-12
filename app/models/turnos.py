
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

def get_shift_from_user(id):
    """
    Devuelve todos los turnos del usuario con id=id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    turnos = cursor.execute("""SELECT * FROM turno 
                                INNER JOIN vacuna as e ON e.id = turno.id_vacuna 
                                INNER JOIN zona as z ON z.id=turno.id_zona 
                                WHERE id_usuario =? AND estado=?;
                                """, (id,1,)).fetchall()
    conn.close()
    return turnos


def cancel_shift(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE turno SET estado=4 WHERE id =?;",(id,))
    conn.commit()
    conn.close()