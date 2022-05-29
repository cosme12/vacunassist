import hashlib
import random
import sqlite3
import string
from datetime import date
from app.models import get_db_connection
import time
from app.models.turnos import tiene_turno_pendiente
from app.models.vacunas import get_id_vacuna, get_vacuna

from app.models.vacunas_aplicadas import tiene_vacuna_aplicada, tiene_vacuna_gripe

def existe_usuario(nombre):
    """
    Devuelve True si el usuario existe en la base de datos
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select COUNT('nombre') from usuario where nombre=?;", (nombre,))
    existe = cursor.fetchone()[0]
    conn.close()
    return existe


def get_usuarios():
    """
    Devuelve todos los usuarios
    """
    conn = get_db_connection()  # Me conecto a la db
    cursor = conn.cursor()  # Creo un cursor para poder ejecutar comandos SQL
    usuarios = cursor.execute("select * from usuario;").fetchall()
    conn.close()
    return usuarios


def guardar_usuario(form_data):
    """
    Guarda un nuevo ususario en la base de datos. Solo se usa para pacientes

    :param form_data: datos del formulario
    """
    conn = get_db_connection()  # Me conecto a la db
    cursor = conn.cursor()  # Creo un cursor para poder ejecutar comandos SQL
    # Genera un string random de 4 caracteres con a-Z y 0-9
    token = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(4)])
    error = None
    try:
        cursor.execute("INSERT INTO usuario (nombre, apellido, dni, email, password, fecha_de_nacimiento, \
                               telefono, paciente_de_riesgo, tipo, token) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                              (form_data['nombre'], form_data['apellido'], form_data['dni'], form_data['email'],
                                hashear_contrasena(form_data['password']), form_data['fecha_de_nacimiento'].strftime('%d/%m/%Y'), form_data['telefono'],
                                form_data['paciente_de_riesgo'], 1, token)).fetchall()
        conn.commit()
    except sqlite3.IntegrityError:
        error = "El usuario ya existe."
    conn.close()
    return error, token


def guardar_enfermero(form_data):
    """
    Guarda un nuevo enfermero en la base de datos

    :param form_data: datos del formulario
    """
    conn = get_db_connection()  # Me conecto a la db
    cursor = conn.cursor()  # Creo un cursor para poder ejecutar comandos SQL
    error = None
    try:
        cursor.execute("INSERT INTO usuario (nombre, apellido, dni, email, password, tipo, id_zona) VALUES (?, ?, ?, ?, ?, ?, ?);",
                              (form_data['nombre'], form_data['apellido'], form_data['dni'], form_data['email'],
                                hashear_contrasena(form_data['dni']), 2, form_data['id_zona'])).fetchall()
        conn.commit()
    except sqlite3.IntegrityError:
        error = "El usuario ya existe."
    conn.close()
    return error


def guardar_vacunas_aplicadas(form_data, id_usuario):
    """
    Guarda un nuevo ususario en la base de datos

    :param form_data: datos del formulario
    :param id_usuario: id del usuario
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    for vacuna in form_data["vacunas"]:
        cursor.execute("INSERT INTO vacuna_aplicada (fecha, id_vacuna, id_usuario) VALUES (?, ?, ?);",
                        (vacuna['fecha_aplicacion'].strftime('%d/%m/%Y'), vacuna['id_vacuna'], id_usuario)).fetchall()
    conn.commit()
    conn.close()    


def hashear_contrasena(contrasena):
    """
    Devuelve un hash de la contraseña
    """
    return hashlib.sha256(str(contrasena).encode('utf8')).hexdigest()


def validar_contrasena(contrasena, contrasena_hash):
    """
    Verifica si la contraseña ingresada es igual a la almacenada en el archivo devuelve True
    """
    return hashear_contrasena(contrasena) == contrasena_hash


def get_user_data(usuario):
    """
    Devuelve los datos del usuario
    """
    conn = get_db_connection() 
    cursor = conn.cursor()  
    user_data = cursor.execute("SELECT * FROM usuario WHERE dni =?;", (usuario,)).fetchone()
    conn.close()
    return user_data


def validar_inicio_sesion(dni, contrasena, token=None):
    """
    Verifica el inicio de sesion de un paciente
    """
    usuario = get_user_data(dni)
    if usuario:
        if usuario["tipo"] == 1:  # Si es un paciente
            if token and usuario["token"] == token and validar_contrasena(contrasena, usuario["password"]):
                return True, "Inicio de sesion correcto"
            else:
                return False, "Credenciales inválidas"
        else: # Verifica si es enfermero o administrador
            if (usuario["tipo"] == 2 or usuario["tipo"] == 3) and validar_contrasena(contrasena, usuario["password"]): 
                return True, "Inicio de sesion correcto"
            else:
                return False, "Credenciales inválidas"
    else:
        return False, "El usuario no está registrado"

def delete_user(id):
    """
    Elimina un usuario con id=id de la tabla usuario.
    """
    conn = get_db_connection() 
    cursor = conn.cursor()  
    user_data = cursor.execute("DELETE FROM usuario WHERE id =?;", (id,))
    conn.commit()
    conn.close()



def edad_de_usuario(id_usuario):
    """
    Devuelve una lista con un solo elemento conteniendo la edad del usuario
    """
    conn= get_db_connection()
    cursor = conn.cursor()
    user_data = cursor.execute("SELECT * FROM usuario WHERE id =?;", (id_usuario,)).fetchone()
    conn.close()
    fecha_de_nacimiento = user_data["fecha_de_nacimiento"].split("/")
    # Cada elemento de fecha_de_nacimiento a int
    fecha_de_nacimiento = [int(i) for i in fecha_de_nacimiento]
    today = date.today()
    edad = today.year - fecha_de_nacimiento[2] - ((today.month, today.day) < (fecha_de_nacimiento[1], fecha_de_nacimiento[0]))
    return edad


def cambiar_password(id, password_nueva):
    hash_password = hashear_contrasena(password_nueva)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuario SET password=? WHERE dni=?;", (hash_password, id,))
    conn.commit()
    conn.close()


def generar_reset_password_token(id_usuario):
    token = str(time.time()) + "supersecreto"
    token = hashear_contrasena(token)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuario SET reset_password_token=? WHERE id=?;", (token, id_usuario,))
    conn.commit()
    conn.close()
    return token

def verificar_reset_password_token(token):
    conn = get_db_connection()
    cursor = conn.cursor()
    usuario = cursor.execute("SELECT * FROM usuario WHERE reset_password_token=?;", (token,)).fetchone()
    conn.close()
    return usuario

def apto_vacuna_covid(id):
    id_covid1 = 4
    id_covid2 = 3
    conn = get_db_connection()
    cursor = conn.cursor()
    dosis2 = tiene_vacuna_aplicada(id, id_covid2)
    if not dosis2:
        turno = tiene_turno_pendiente(id, id_covid1) or tiene_turno_pendiente(id, id_covid2)
        return not turno
    return False

def apto_vacuna_gripe(id):
    id_gripe = 1
    conn = get_db_connection()
    cursor = conn.cursor()
    vacuna = tiene_vacuna_gripe(id)
    if not vacuna:
        turno = tiene_turno_pendiente(id, id_gripe)
        return not turno
    return False

def apto_vacuna_fiebre_amarilla(id):
    id_fiebre_amarilla = 2
    conn = get_db_connection()
    cursor = conn.cursor()
    edad = edad_de_usuario(id)
    if edad < 60:
        vacuna = tiene_vacuna_aplicada(id, id_fiebre_amarilla)
        if not vacuna:
            turno = tiene_turno_pendiente(id, id_fiebre_amarilla)
            return not turno
    return False

def tiene_covid1(id):
    id_covid1 = 4
    conn = get_db_connection()
    cursor = conn.cursor()
    return tiene_vacuna_aplicada(id, id_covid1)
    