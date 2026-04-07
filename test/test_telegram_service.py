from src.services.telegram_service import handle_command, handle_update


def test_handle_start_command():
    response = handle_command("123", "/start")
    assert "Welcome" in response


def test_handle_help_command():
    response = handle_command("123", "/help")
    assert "/start" in response and "/help" in response


def test_handle_echo_command():
    response = handle_command("123", "/echo hello world")
    assert response == "hello world"


def test_handle_summarize_command(monkeypatch):
    monkeypatch.setattr(
        "src.services.telegram_service.summarize_text",
        lambda text: {"summary": "short summary", "language": "en"},
    )
    response = handle_command("123", "/summarize this text")
    assert "Summary" in response
    assert "short summary" in response


def test_handle_update_no_message():
    result = handle_update({})
    assert result["status"] == "ignored"


def test_handle_update_text_only(monkeypatch):
    payload = {"message": {"chat": {"id": 123}, "text": "/help"}}
    monkeypatch.setattr(
        "src.services.telegram_service.send_message",
        lambda chat_id, text, reply_markup=None: {"status": "sent", "text": text},
    )
    result = handle_update(payload)
    assert result["status"] == "sent"
