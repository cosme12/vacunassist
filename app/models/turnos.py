
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

    
def reservar_turno(fecha,id_usuario,id_vacuna, id_zona):
    estado_turno = 2
    if id_vacuna == 2:
        estado_turno = 1
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO turno (fecha,estado, id_usuario, id_vacuna, id_zona)\
                     VALUES ( ?, ?, ?, ?, ?);",(fecha,estado_turno,id_usuario,id_vacuna,id_zona,))
    conn.commit()
    conn.close()

def tiene_turno_pendiente(id_usuario, id_vacuna):
    conn = get_db_connection()
    cursos = conn.cursor()
    turnos = cursos.execute("SELECT * FROM turno WHERE id_usuario=? and id_vacuna=?;",(id_usuario, id_vacuna,)).fetchall()
    conn.close()
    for turno in turnos:
        if (turno["estado"] == 1 or turno["estado"] == 2):
            return True 
    return False
