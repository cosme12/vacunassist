
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

def get_appointment_from_user(id):
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


def tiene_appointment_covid1_from_user(id):
    """
    Indica si tiene turno de covid1 reservado para el usuario con id=id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    turnos = cursor.execute("""SELECT COUNT(*) FROM turno 
                                INNER JOIN vacuna as e ON e.id = turno.id_vacuna  
                                INNER JOIN zona as z ON z.id=turno.id_zona 
                                WHERE id_usuario =? AND estado=? AND id_vacuna=?;
                                """, (id, 1, 4)).fetchone()
    if turnos[0] > 0:
        turnos = True
    else:
        turnos = False
    conn.close()
    return turnos


def cancel_appointment(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE turno SET estado=4 WHERE id =?;",(id,))
    conn.commit()
    conn.close()