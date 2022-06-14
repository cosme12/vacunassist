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


def aplicar_vacunas(paciente_nuevo):
    vacunas_aplicadas = [
        {
            'fecha': '04/01/2020',
            'laboratorio': 'Laboratorio 1',
            'lote': 'Lote 1',
            'id_vacuna': 1,
            'id_usuario': 1,
            'id_zona': 2
        },
        {
            'fecha': '14/03/2020',
            'laboratorio': 'Laboratorio 2',
            'lote': 'Lote 2',
            'id_vacuna': 2,
            'id_usuario': 1,
            'id_zona': 2
        },
        {
            'fecha': '19/03/2022',
            'laboratorio': None,
            'lote': None,
            'id_vacuna': 4,
            'id_usuario': 1,
            'id_zona': 3
        }
    ]
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    cursor = conn.cursor()
    for vacuna in vacunas_aplicadas:
        cursor.execute("INSERT INTO vacuna_aplicada (fecha, lote, laboratorio, id_vacuna, id_usuario, id_zona) VALUES (?, ?, ?, ?, ?, ?);",
                              (vacuna['fecha'], vacuna['lote'], vacuna['laboratorio'], vacuna['id_vacuna'], vacuna['id_usuario'], vacuna['id_zona']))
    conn.commit()
    conn.close()
    return vacunas_aplicadas


def test_mis_vacunas_route_sin_vacunas_aplicadas(client, create_db):
    paciente_nuevo = crear_usuario_paciente()

    # Inicia sesion
    with client:
        response = client.post('/login', data={
            'dni': paciente_nuevo['dni'],
            'password': '12345',
            'token': paciente_nuevo['token']
        }, follow_redirects=True)
        response = client.get("/mis-vacunas")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Cerrar sesión' in html
        assert 'Mi perfil' in html
        assert 'Mis vacunas' in html
        assert 'Mis turnos' in html
        assert 'No tiene vacunas aplicadas' in html


def test_mis_vacunas_route_con_vacunas_aplicadas(client, create_db):
    paciente_nuevo = crear_usuario_paciente()
    vacunas_aplicadas = aplicar_vacunas(paciente_nuevo)

    # Inicia sesion
    with client:
        response = client.post('/login', data={
            'dni': paciente_nuevo['dni'],
            'password': '12345',
            'token': paciente_nuevo['token']
        }, follow_redirects=True)
        response = client.get("/mis-vacunas")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Cerrar sesión' in html
        assert 'Mi perfil' in html
        assert 'Mis vacunas' in html
        assert 'Mis turnos' in html
        assert 'No tiene vacunas aplicadas' not in html
        assert vacunas_aplicadas[0]['fecha'] in html
        assert vacunas_aplicadas[0]['laboratorio'] in html
        assert vacunas_aplicadas[0]['lote'] in html
        assert vacunas_aplicadas[1]['fecha'] in html
        assert vacunas_aplicadas[1]['laboratorio'] in html
        assert vacunas_aplicadas[1]['lote'] in html
        assert vacunas_aplicadas[2]['fecha'] in html
        assert 'Vacuna administrada por fuera del vacunatorio' in html
        assert 'GRIPE' in html
        assert 'FIEBRE AMARILLA' in html
        assert 'COVID PRIMERA DOSIS' in html
        assert 'Generar certificado' in html
        assert 'None' not in html


def test_mis_vacunas_route_sin_iniciar_sesion(client, create_db):
    crear_usuario_paciente()
    with client:
        response = client.get("/mis-vacunas", follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == "/login"

