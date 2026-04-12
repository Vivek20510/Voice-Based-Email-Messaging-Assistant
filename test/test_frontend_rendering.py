import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_dashboard_renders(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["user_email"] = "test@example.com"

    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    response = client.get("/dashboard")
    assert response.status_code == 200
    assert b"Unified Inbox" in response.data
    assert b"Voice Assistant" in response.data
    assert b"Quick reply" in response.data
    assert b"Gmail" in response.data


def test_login_page_renders(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Welcome back" in response.data
    assert b"Continue with Google" in response.data


def test_base_template_includes_static_files(client):
    response = client.get("/")
    # Since not logged in, should show login
    response = client.get("/auth/login")
    assert b"style.css" in response.data
    assert b"app.js" in response.data
