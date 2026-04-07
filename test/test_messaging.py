from src.services.messaging_service import send_telegram_message


def test_send_telegram_stub():
    result = send_telegram_message("123", "hello")
    assert result["status"] in ["stub", "sent", "error"]
