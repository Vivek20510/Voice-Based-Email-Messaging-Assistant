from src.services.email_service import send_email, list_emails, read_email


def test_send_email_stub(monkeypatch):
    monkeypatch.setenv("GMAIL_API_ENABLED", "false")
    result = send_email("a@example.com", "subject", "body")
    assert result["status"] == "stub"


def test_list_emails_stub(monkeypatch):
    monkeypatch.setenv("GMAIL_API_ENABLED", "false")
    result = list_emails(1)
    assert result["status"] == "stub"
    assert isinstance(result["messages"], list)
    assert isinstance(result["emails"], list)


def test_read_email_stub(monkeypatch):
    monkeypatch.setenv("GMAIL_API_ENABLED", "false")
    result = read_email(1, "123")
    assert result["status"] == "stub"
    assert result["message_id"] == "123"


def test_list_emails_auth_required(monkeypatch):
    monkeypatch.setenv("GMAIL_API_ENABLED", "true")
    result = list_emails(None)
    assert result["status"] == "error"
    assert "Authentication required" in result["message"]


def test_read_email_auth_required(monkeypatch):
    monkeypatch.setenv("GMAIL_API_ENABLED", "true")
    result = read_email(None, "123")
    assert result["status"] == "error"
    assert "Authentication required" in result["message"]


def test_list_emails_returns_preview_payload(monkeypatch):
    monkeypatch.setenv("GMAIL_API_ENABLED", "true")
    monkeypatch.setattr(
        "src.services.email_service.get_token",
        lambda user_id, service: {"access_token": "token"},
    )
    monkeypatch.setattr(
        "src.services.email_service.fetch_message_summaries",
        lambda token, user_id, register_token: [
            {
                "id": "msg-1",
                "from": "sender@example.com",
                "subject": "Hello",
                "preview": "Preview text",
                "date": "2026-04-12T10:30:00Z",
                "channel": "email",
            }
        ],
    )

    result = list_emails(1)

    assert result["status"] == "ok"
    assert result["messages"][0]["subject"] == "Hello"
    assert result["emails"][0]["from"] == "sender@example.com"
