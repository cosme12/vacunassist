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


def test_login_redirect_no_iniciado_sesion(client):
    response = client.get("/", follow_redirects=True)
    # Check that there was one redirect response.
    assert len(response.history) == 1
    # Check that the second request was to the index page.
    assert response.request.path == "/login"




