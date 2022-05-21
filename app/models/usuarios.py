import hashlib
import random
import sqlite3
import string
from datetime import datetime
from app.models import get_db_connection


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
    Guarda un nuevo ususario en la base de datos

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
        else:
            # Verificar si es enfermero o administrador
            pass
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

    conn= get_db_connection()
    cursor = conn.cursor()
    edad = cursor.execute("SELECT (julianday('now') - julianday( fecha_de_nacimiento) ) / 365 as edad,\
        fecha_de_nacimiento FROM usuario WHERE id=?;",(id_usuario,)).fetchone()
    
    conn.close()
    return edad

def cambiar_password(id, password_nueva):
    hash_password = hashear_contrasena(password_nueva)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE usuario SET password=? WHERE dni=?;", (hash_password, id,))
    conn.commit()
    conn.close()
