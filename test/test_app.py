import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_send_email_stub(client):
    response = client.post(
        "/email/send", json={"to": "a@example.com", "subject": "hi", "body": "hello"}
    )
    assert response.status_code == 200
    assert response.json["status"] in ["stub", "error"]


def test_send_telegram_missing(client):
    response = client.post(
        "/message/telegram", json={"chat_id": "123", "text": "hello"}
    )
    assert response.status_code == 200
    assert response.json["status"] in ["stub", "sent", "error"]


def test_nlp_routes(client, monkeypatch):
    # Mock summarize and suggest behavior to avoid heavy model loads

    monkeypatch.setattr(
        "src.app.summarize_text", lambda text: {"summary": "summary", "language": "en"}
    )
    monkeypatch.setattr(
        "src.app.suggest_replies",
        lambda text: {"replies": "reply1;reply2", "language": "en"},
    )

    response = client.post("/nlp/summarize", json={"text": "please summarize this"})
    assert response.status_code == 200
    assert response.json == {"summary": "summary", "language": "en"}

    response = client.post("/nlp/suggest", json={"text": "please suggest"})
    assert response.status_code == 200
    assert response.json == {"replies": "reply1;reply2", "language": "en"}


def test_email_status(client):
    response = client.get("/email/status")
    assert response.status_code == 200
    assert "email_api" in response.json
