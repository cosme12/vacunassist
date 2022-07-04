
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


def get_turno_por_id(id_turno):
    """
    Devuelve un determinado turno
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    turno = cursor.execute("select * from turno where id=?;",(id_turno,)).fetchone()
    conn.close()
    return turno


def get_turnos_aprobados():
    """
    Devuelve todos los turnos aprobados (con estado 2)
    """
    conn = get_db_connection()
    cursos = conn.cursor()
    turnos = cursos.execute("""SELECT * FROM turno as t INNER JOIN usuario as u ON t.id_usuario = u.id
                            INNER JOIN vacuna as v ON t.id_vacuna = v.id
                            INNER JOIN zona as z ON t.id_zona = z.id
                            WHERE estado=?;""",(2,)).fetchall()
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
                                WHERE id_usuario =? AND (estado=? OR estado=?);
                                """, (id,1,2)).fetchall()
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
                                """, (id, 2, 4)).fetchone()
    if turnos[0] > 0:
        turnos = True
    else:
        turnos = False
    conn.close()
    return turnos


def cancel_appointment(id, estado):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE turno SET estado=? WHERE id =?;",(estado, id,))
    conn.commit()
    conn.close()

    
def reservar_turno(fecha,id_usuario,id_vacuna, id_zona, hora):
    estado_turno = 2
    if id_vacuna == 2:
        estado_turno = 1
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO turno (fecha,estado, id_usuario, id_vacuna, id_zona,hora)\
                     VALUES ( ?, ?, ?, ?, ?, ?);",(fecha.strftime('%d/%m/%Y'),estado_turno,id_usuario,id_vacuna,id_zona,hora.strftime("%H:%M"),))
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

def get_turnos_del_dia(fecha, zona):
    conn = get_db_connection()
    cursos = conn.cursor()
    turnos = cursos.execute("SELECT t.id, t.fecha, t.hora, t.id_usuario, t.id_vacuna, \
                            u.dni, u.nombre, u.apellido, u.fecha_de_nacimiento, u.paciente_de_riesgo, \
                            z.nombre as zona, v.enfermedad as vacuna \
                            FROM turno AS t \
                            INNER JOIN usuario AS u ON t.id_usuario=u.id \
                            INNER JOIN vacuna AS v ON t.id_vacuna=v.id \
                            INNER JOIN zona AS z ON t.id_zona=z.id \
                            WHERE t.fecha=? and t.estado=? and t.id_zona=? \
                            ORDER BY t.hora, u.apellido;", (fecha, 2, zona,)).fetchall()
    conn.close()
    return turnos

def finalizar_turno(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE turno SET estado=3 WHERE id =?;",(id,))
    conn.commit()
    conn.close()


def get_pendientes_fiebre_amarilla():
    conn = get_db_connection()
    cursos = conn.cursor()
    turnos = cursos.execute("SELECT t.id, t.fecha, t.hora, t.id_usuario, t.id_vacuna, \
                            u.dni, u.nombre, u.apellido, u.fecha_de_nacimiento, u.paciente_de_riesgo, \
                            z.nombre as zona, v.enfermedad as vacuna \
                            FROM turno AS t \
                            INNER JOIN usuario AS u ON t.id_usuario=u.id \
                            INNER JOIN vacuna AS v ON t.id_vacuna=v.id \
                            INNER JOIN zona AS z ON t.id_zona=z.id \
                            WHERE t.id_vacuna = 2 and t.estado=1 \
                            ORDER BY t.hora, u.apellido;").fetchall()
    conn.close()
    return turnos

def aprobar_turno(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE turno SET estado=2 WHERE id =?;",(id,))
    conn.commit()
    conn.close()


def get_cant_turnos_por_zona():
    """
    Devuelve la cantidad de turnos pendientes para los proximos 7 dias para cada zona
    """
    conn = get_db_connection()
    cursos = conn.cursor()
    turnos = cursos.execute("SELECT z.id, z.nombre as zona, count(t.id) as cantidad \
                            FROM zona AS z \
                            LEFT JOIN turno AS t ON (z.id=t.id_zona and t.estado=2 and DATE(substr(t.fecha,7,4) \
                            ||'-' || substr(t.fecha,4,2) || '-' || substr(t.fecha,1,2)) >= date('now') \
                            and DATE(substr(t.fecha,7,4) ||'-' || substr(t.fecha,4,2) || '-' || substr(t.fecha,1,2)) <= date('now', '+7 days')) \
                            GROUP BY z.id;").fetchall()
    conn.close()
    return turnos

def get_turnos_cancelados_por_vacuna(id_vacuna):
    """
    Devuelve los turnos cancelados para la vacuna con id=id_vacuna
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    turnos = cursor.execute("SELECT * FROM turno WHERE id_vacuna=? AND (estado=? OR estado=?);", (id_vacuna, 4, 5,)).fetchall()
    conn.close()
    return turnos
