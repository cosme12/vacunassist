import pytest, sqlite3
from flask import session
from app import app as flask_app


def debuggear_respuesta(html):
    """
    Funcion para debuguear el html de la respuesta
    """
    with open('tests/log.html', 'w') as f:
        f.write(html)


@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "password-super-dificil",
        "WTF_CSRF_ENABLED": False,  # no CSRF during tests
        "DATABASE": "tests/testdb.db",
        "EMAIL_ENABLED": False
    })

    # other setup can go here
    yield flask_app
    # clean up / reset resources here


@pytest.fixture()
def create_db(app):
    conn = sqlite3.connect(app.config['DATABASE']) 
    cursor = conn.cursor()
    with open('tests/testdb.sql', 'r') as f:
        cursor.executescript(f.read())
    conn.close()


@pytest.fixture()
def client(app):
    return app.test_client()



def crear_usuario_paciente():
    """
    Crea un usuario paciente en la db
    """
    paciente_nuevo = {
        'dni': '00000002',
        'nombre': 'Rogelio',
        'apellido': 'Perez',
        'email': 'juanperez@example.com',
        'password': '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5',
        'fecha_de_nacimiento': '01/05/2005',
        'telefono': '123456789',
        'paciente_de_riesgo': False,
        'token': '1x3A',
        'tipo': 1
    }
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuario (nombre, apellido, dni, email, password, fecha_de_nacimiento, \
                               telefono, paciente_de_riesgo, tipo, token) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                              (paciente_nuevo['nombre'], paciente_nuevo['apellido'], paciente_nuevo['dni'], paciente_nuevo['email'],
                                paciente_nuevo['password'], paciente_nuevo['fecha_de_nacimiento'], paciente_nuevo['telefono'],
                                paciente_nuevo['paciente_de_riesgo'], paciente_nuevo['tipo'], paciente_nuevo['token']))
    conn.commit()
    conn.close()
    return paciente_nuevo


def crear_usuario_paciente_mayor_60():
    """
    Crea un usuario paciente en la db
    """
    paciente_nuevo = {
        'dni': '00000005',
        'nombre': 'Rogelio',
        'apellido': 'Perez',
        'email': 'juanperez@example.com',
        'password': '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5',
        'fecha_de_nacimiento': '01/05/1940',
        'telefono': '123456789',
        'paciente_de_riesgo': False,
        'token': '1x3A',
        'tipo': 1
    }
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuario (nombre, apellido, dni, email, password, fecha_de_nacimiento, \
                               telefono, paciente_de_riesgo, tipo, token) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                              (paciente_nuevo['nombre'], paciente_nuevo['apellido'], paciente_nuevo['dni'], paciente_nuevo['email'],
                                paciente_nuevo['password'], paciente_nuevo['fecha_de_nacimiento'], paciente_nuevo['telefono'],
                                paciente_nuevo['paciente_de_riesgo'], paciente_nuevo['tipo'], paciente_nuevo['token']))
    conn.commit()
    conn.close()
    return paciente_nuevo


def crear_usuario_paciente_riesgo():
    """
    Crea un usuario paciente en la db
    """
    paciente_nuevo = {
        'dni': '00000002',
        'nombre': 'Rogelio',
        'apellido': 'Perez',
        'email': 'juanperez@example.com',
        'password': '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5',
        'fecha_de_nacimiento': '01/05/2005',
        'telefono': '123456789',
        'paciente_de_riesgo': True,
        'token': '1x3A',
        'tipo': 1
    }
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuario (nombre, apellido, dni, email, password, fecha_de_nacimiento, \
                               telefono, paciente_de_riesgo, tipo, token) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                              (paciente_nuevo['nombre'], paciente_nuevo['apellido'], paciente_nuevo['dni'], paciente_nuevo['email'],
                                paciente_nuevo['password'], paciente_nuevo['fecha_de_nacimiento'], paciente_nuevo['telefono'],
                                paciente_nuevo['paciente_de_riesgo'], paciente_nuevo['tipo'], paciente_nuevo['token']))
    conn.commit()
    conn.close()
    return paciente_nuevo


def crear_turno_covid():
    """
    Crear turno de covid en la db
    """
    turno = {
        'fecha': '03/05/2020',
        'estado': 2,
        'hora': '05:00',
        'id_usuario': 1,
        'id_vacuna': 4,
        'id_zona': 1
    }
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    cursor = conn.cursor()
    cursor.execute("INSERT INTO turno (fecha, estado, hora, id_usuario, id_vacuna, id_zona) VALUES (?, ?, ?, ?, ?, ?);",
                              (turno['fecha'], turno['estado'], turno['hora'], turno['id_usuario'],
                                turno['id_vacuna'], turno['id_zona']))
    conn.commit()
    conn.close()
    return turno


def test_login_form(client):
    response = client.get("/login")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Inicie sesión' in html
    assert 'name="dni"' in html
    assert 'name="password"' in html
    assert 'name="token"' in html


def test_inicio_de_sesion_paciente_registrado(client, create_db):
    # Crea paciente en la db
    paciente_nuevo = crear_usuario_paciente()

    # Inicia sesion
    response = client.post('/login', data={
        'dni': paciente_nuevo['dni'],
        'password': '12345',
        'token': paciente_nuevo['token']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/"
    html = response.get_data(as_text=True)
    assert 'Cerrar sesión' in html
    assert 'Perfil' in html
    assert 'Mis vacunas' in html
    assert 'Mis turnos' in html


def test_inicio_de_sesion_paciente_registrado_sesion(client, create_db):
    # Crea paciente en la db
    paciente_nuevo = crear_usuario_paciente()

    # Inicia sesion
    with client:
        response = client.post('/login', data={
            'dni': paciente_nuevo['dni'],
            'password': '12345',
            'token': paciente_nuevo['token']
        }, follow_redirects=True)
        assert response.status_code == 200
        assert session["dni"] == paciente_nuevo['dni']


def test_inicio_de_sesion_paciente_registrado_sin_token(client, create_db):
    # Crea paciente en la db
    paciente_nuevo = crear_usuario_paciente()

    # Inicia sesion
    response = client.post('/login', data={
        'dni': paciente_nuevo['dni'],
        'password': '12345'
    }, follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Cerrar sesión' not in html
    assert 'Perfil' not in html
    assert 'Mis vacunas' not in html
    assert 'Mis turnos' not in html
    assert 'Credenciales inválidas' in html


def test_inicio_de_sesion_paciente_no_registrado_sin_token(client, create_db):
    # Crea paciente en la db
    paciente_nuevo = crear_usuario_paciente()

    # Inicia sesion
    response = client.post('/login', data={
        'dni': '9999',
        'password': '12345'
    }, follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Cerrar sesión' not in html
    assert 'Perfil' not in html
    assert 'Mis vacunas' not in html
    assert 'Mis turnos' not in html
    assert 'El usuario no está registrado' in html


def test_inicio_de_sesion_paciente_no_registrado_con_token(client, create_db):
    # Crea paciente en la db
    paciente_nuevo = crear_usuario_paciente()

    # Inicia sesion
    response = client.post('/login', data={
        'dni': '9999',
        'password': '12345',
        'token': paciente_nuevo['token']
    }, follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Cerrar sesión' not in html
    assert 'Perfil' not in html
    assert 'Mis vacunas' not in html
    assert 'Mis turnos' not in html
    assert 'El usuario no está registrado' in html


def test_inicio_de_sesion_paciente_registrado_sin_covid_de_riesgo(client, create_db):
    # Crea paciente en la db
    paciente_nuevo = crear_usuario_paciente_riesgo()

    # Inicia sesion
    response = client.post('/login', data={
        'dni': paciente_nuevo['dni'],
        'password': '12345',
        'token': paciente_nuevo['token']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/sacar-turno/4"
    html = response.get_data(as_text=True)
    assert 'Cerrar sesión' in html
    assert 'Perfil' in html
    assert 'Mis vacunas' in html
    assert 'Mis turnos' in html
    assert 'Reservar turno para vacuna de Covid PRIMERA DOSIS' in html


def test_inicio_de_sesion_paciente_registrado_sin_covid_60(client, create_db):
    # Crea paciente en la db
    paciente_nuevo = crear_usuario_paciente_mayor_60()

    # Inicia sesion
    response = client.post('/login', data={
        'dni': paciente_nuevo['dni'],
        'password': '12345',
        'token': paciente_nuevo['token']
    }, follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == "/sacar-turno/4"
    html = response.get_data(as_text=True)
    assert 'Cerrar sesión' in html
    assert 'Perfil' in html
    assert 'Mis vacunas' in html
    assert 'Mis turnos' in html
    assert 'Reservar turno para vacuna de Covid PRIMERA DOSIS' in html


def test_inicio_de_sesion_paciente_registrado_con_covid_60(client, create_db):
    # Crea paciente en la db
    paciente_nuevo = crear_usuario_paciente_mayor_60()
    crear_turno_covid()

    # Inicia sesion
    response = client.post('/login', data={
        'dni': paciente_nuevo['dni'],
        'password': '12345',
        'token': paciente_nuevo['token']
    }, follow_redirects=True)
    assert response.status_code == 200
    #assert response.request.path == "/sacar-turno/1"
    html = response.get_data(as_text=True)
    #debuggear_respuesta(html)
    assert 'Cerrar sesión' in html
    assert 'Perfil' in html
    assert 'Mis vacunas' in html
    assert 'Mis turnos' in html
    assert 'Reservar turno para vacuna de Gripe' in html

