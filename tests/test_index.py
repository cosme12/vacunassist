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


def test_login_redirect_no_iniciado_sesion(client):
    response = client.get("/", follow_redirects=True)
    # Check that there was one redirect response.
    assert len(response.history) == 1
    # Check that the second request was to the index page.
    assert response.request.path == "/login"




