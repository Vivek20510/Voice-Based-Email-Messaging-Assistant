import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_telegram_ping(client):
    response = client.get("/telegram/ping")
    assert response.status_code == 200
    assert response.json == {"status": "ok", "message": "Telegram webhook is active."}


def test_telegram_webhook_invalid_payload(client):
    response = client.post("/telegram/webhook", json=None)
    assert response.status_code == 400
    assert response.json["status"] == "error"
