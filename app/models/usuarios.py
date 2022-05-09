import hashlib
import sqlite3
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
    error = None
    try:
        cursor.execute("INSERT INTO usuario (nombre, apellido, dni, email, password, fecha_de_nacimiento, \
                               telefono, paciente_de_riesgo, tipo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
                              (form_data['nombre'], form_data['apellido'], form_data['dni'], form_data['email'],
                                hashear_contrasena(form_data['password']), form_data['fecha_de_nacimiento'], form_data['telefono'],
                                form_data['paciente_de_riesgo'], 1)).fetchall()
        conn.commit()
    except sqlite3.IntegrityError:
        error = "El usuario ya existe."
    conn.close()
    return error


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
