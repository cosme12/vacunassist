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



def iniciar_sesion(client, paciente_nuevo):
    response = client.get('/login', data={
            'dni': paciente_nuevo['dni'],
            'password': '12345',
            'token': paciente_nuevo['token']
        }, follow_redirects=True)
    return response


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


def test_perfil_route(client, create_db):
    paciente_nuevo = crear_usuario_paciente()

    # Inicia sesion
    with client:
        response = client.post('/login', data={
            'dni': paciente_nuevo['dni'],
            'password': '12345',
            'token': paciente_nuevo['token']
        }, follow_redirects=True)
        response = client.get("/perfil")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Cerrar sesión' in html
        assert 'Perfil' in html
        assert 'Mis vacunas' in html
        assert 'Mis turnos' in html
        assert paciente_nuevo['nombre'] in html
        assert paciente_nuevo['apellido'] in html
        assert paciente_nuevo['dni'] in html
        assert paciente_nuevo['email'] in html
        assert paciente_nuevo['fecha_de_nacimiento'] in html
        assert 'CAMBIAR CONTRASEÑA' in html
        assert 'ELIMINAR CUENTA' in html


def test_perfil_route_sin_iniciar_sesion(client, create_db):
    crear_usuario_paciente()
    with client:
        response = client.get("/perfil", follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == "/login"

