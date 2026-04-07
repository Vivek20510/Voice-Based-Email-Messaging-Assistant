import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_dashboard_renders(client):
    response = client.get("/?user_email=test@example.com")
    assert response.status_code == 302

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_email"] = "test@example.com"

    response = client.get("/")
    assert response.status_code == 200
    assert b"Voice Email Assistant" in response.data
    assert b"test@example.com" in response.data
    assert b"Voice Email Assistant Dashboard" in response.data
    assert b"Start Recording" in response.data


def test_login_page_renders(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_base_template_includes_static_files(client):
    response = client.get("/")
    # Since not logged in, should show login
    response = client.get("/auth/login")
    assert b"style.css" in response.data
    assert b"app.js" in response.data
