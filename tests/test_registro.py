import pytest, sqlite3
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
        "DATABASE": "tests/testdb.db"
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


def test_login_form(client):
    response = client.get("/registro")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Registro' in html
    assert 'name="dni"' in html
    assert 'name="nombre"' in html
    assert 'name="apellido"' in html
    assert 'name="email"' in html
    assert 'name="password"' in html
    assert 'name="confirmar"' in html
    assert 'name="fecha_de_nacimiento"' in html
    assert 'name="telefono"' in html
    assert 'name="paciente_de_riesgo"' in html


def test_registrar_paciente_sin_historial(client, create_db):
    response = client.post('/registro', data={
        'dni': '00000001',
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'juanperez@example.com',
        'password': '12345',
        'confirmar': '12345',
        'fecha_de_nacimiento': '2000-01-01',
        'telefono': '123456789',
        'paciente_de_riesgo': True
    }, follow_redirects=True)
    assert response.status_code == 200
    #debuggear_respuesta(response.get_data(as_text=True))
    assert response.request.path == '/login' # redirected to login
    html = response.get_data(as_text=True)
    assert f'El registro fue exitoso. Hemos enviado un mail a juanperez@example.com con un token que deberá usar junto con su contraseña para iniciar sesión.' in html

    # Verifica que los datos del usuario se hayan guardado en la base de datos
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    paciente = cursor.execute("SELECT * FROM usuario WHERE dni = '00000001'").fetchone()
    conn.close()
    assert paciente is not None
    assert paciente["nombre"] == 'Juan'
    assert paciente["apellido"] == 'Perez'
    assert paciente["password"] == '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5'
    assert paciente["email"] == 'juanperez@example.com'
    assert paciente["fecha_de_nacimiento"] == '01/01/2000'
    assert paciente["telefono"] == '123456789'
    assert paciente["paciente_de_riesgo"] == 1
    assert paciente["tipo"] == 1

    # Verifica que no se hayan cargado ningun dato en vacunas aplicadas
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    vacunas_aplicadas = cursor.execute("SELECT COUNT(*) FROM vacuna_aplicada").fetchone()
    conn.close()
    assert vacunas_aplicadas[0] == 0


def test_registrar_paciente_con_historial(client, create_db):
    response = client.post('/registro', data={
        'dni': '00000001',
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'juanperez@example.com',
        'password': '12345',
        'confirmar': '12345',
        'fecha_de_nacimiento': '2000-01-01',
        'telefono': '123456789',
        'paciente_de_riesgo': True,
        'vacunas-0-id_vacuna': '1',
        'vacunas-0-fecha_aplicacion': '2020-01-01',
        'vacunas-1-id_vacuna': '2',
        'vacunas-1-fecha_aplicacion': '2020-01-02'
    }, follow_redirects=True)
    assert response.status_code == 200
    #debuggear_respuesta(response.get_data(as_text=True))
    assert response.request.path == '/login' # redirected to login
    html = response.get_data(as_text=True)
    assert f'El registro fue exitoso. Hemos enviado un mail a juanperez@example.com con un token que deberá usar junto con su contraseña para iniciar sesión.' in html

    # Verifica que los datos del usuario se hayan guardado en la base de datos
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    paciente = cursor.execute("SELECT * FROM usuario WHERE dni = '00000001'").fetchone()
    conn.close()
    assert paciente is not None
    assert paciente["nombre"] == 'Juan'
    assert paciente["apellido"] == 'Perez'
    assert paciente["password"] == '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5'
    assert paciente["email"] == 'juanperez@example.com'
    assert paciente["fecha_de_nacimiento"] == '01/01/2000'
    assert paciente["telefono"] == '123456789'
    assert paciente["paciente_de_riesgo"] == 1
    assert paciente["tipo"] == 1

    # Verifica que se hayan cargado las vacunas aplicadas
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    vacunas_aplicadas = cursor.execute("SELECT * FROM vacuna_aplicada WHERE id_usuario = 1").fetchall()
    conn.close()
    assert len(vacunas_aplicadas) == 2
    assert vacunas_aplicadas[0]["id_usuario"] == 1
    assert vacunas_aplicadas[0]["id_vacuna"] == 1
    assert vacunas_aplicadas[0]["fecha"] == '01/01/2020'
    assert vacunas_aplicadas[1]["id_usuario"] == 1
    assert vacunas_aplicadas[1]["id_vacuna"] == 2
    assert vacunas_aplicadas[1]["fecha"] == '02/01/2020'
    

def test_registrar_paciente_con_historial_vacunas_repetidas(client, create_db):
    response = client.post('/registro', data={
        'dni': '00000001',
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'juanperez@example.com',
        'password': '12345',
        'confirmar': '12345',
        'fecha_de_nacimiento': '2000-01-01',
        'telefono': '123456789',
        'paciente_de_riesgo': True,
        'vacunas-0-id_vacuna': '1',
        'vacunas-0-fecha_aplicacion': '2020-01-01',
        'vacunas-1-id_vacuna': '1',
        'vacunas-1-fecha_aplicacion': '2020-01-02'
    }, follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert f'No pueden seleccionar más de una vez la misma vacuna.' in html

    # Verifica que los datos del usuario NO se hayan guardado en la base de datos
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    paciente = cursor.execute("SELECT * FROM usuario WHERE dni = '00000001'").fetchone()
    conn.close()
    assert paciente is None

    # Verifica que NO se hayan cargado las vacunas aplicadas
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    vacunas_aplicadas = cursor.execute("SELECT * FROM vacuna_aplicada WHERE id_usuario = 1").fetchall()
    conn.close()
    assert len(vacunas_aplicadas) == 0


def test_registrar_paciente_con_historial_sin_covid_primera_dosis(client, create_db):
    response = client.post('/registro', data={
        'dni': '00000001',
        'nombre': 'Juan',
        'apellido': 'Perez',
        'email': 'juanperez@example.com',
        'password': '12345',
        'confirmar': '12345',
        'fecha_de_nacimiento': '2000-01-01',
        'telefono': '123456789',
        'paciente_de_riesgo': True,
        'vacunas-0-id_vacuna': '3',
        'vacunas-0-fecha_aplicacion': '2020-01-01'
    }, follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert f'Falta seleccionar la primera dosis de la vacuna Covid-19.' in html

    # Verifica que los datos del usuario NO se hayan guardado en la base de datos
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    paciente = cursor.execute("SELECT * FROM usuario WHERE dni = '00000001'").fetchone()
    conn.close()
    assert paciente is None

    # Verifica que NO se hayan cargado las vacunas aplicadas
    conn = sqlite3.connect(flask_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    vacunas_aplicadas = cursor.execute("SELECT * FROM vacuna_aplicada WHERE id_usuario = 1").fetchall()
    conn.close()
    assert len(vacunas_aplicadas) == 0

