# coding: utf-8

import pytest
from app import app as flask_app


@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "password-super-dificil",
    })

    # other setup can go here
    yield flask_app
    # clean up / reset resources here


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




