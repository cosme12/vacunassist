from datetime import date
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
    conn.close()
    return vacunas


def tiene_vacuna_aplicada(id_usuario, id_vacuna):
    conn = get_db_connection()
    cursor = conn.cursor()
    vacuna_aplicada = cursor.execute("SELECT * FROM vacuna_aplicada \
                                    WHERE id_usuario=? and id_vacuna=? ORDER BY id DESC;",(id_usuario,id_vacuna,)).fetchone()
    conn.close()
    if vacuna_aplicada is None:
        return False
    else:
        return True


def tiene_vacuna_gripe(id_usuario):
    conn = get_db_connection()
    cursor = conn.cursor()
    fecha_gripe = cursor.execute("SELECT * FROM vacuna_aplicada WHERE id_vacuna=1 and id_usuario=? ORDER BY ID DESC;",
                                (id_usuario,)).fetchone()
    conn.close()
    if fecha_gripe is None:
        return False
    fecha_aplicacion = fecha_gripe["fecha"].split("/")
    # Cada elemento de fecha_aplicacion a int
    fecha_aplicacion = [int(i) for i in fecha_aplicacion]
    today = date.today()
    anios = today.year - fecha_aplicacion[2] - ((today.month, today.day) < (fecha_aplicacion[1], fecha_aplicacion[0]))
    
    if anios >= 1:
        return False
    else:
        return True

def get_vacuna_aplicada_covid1(id_usuario):
    conn = get_db_connection()
    cursor = conn.cursor()
    vacuna = cursor.execute("SELECT * FROM vacuna_aplicada WHERE id_usuario=? and id_vacuna=4;", (id_usuario,)).fetchone()
    conn.close()
    return vacuna