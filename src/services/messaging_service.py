import os
import requests
from typing import Dict


def send_telegram_message(chat_id: str, text: str) -> Dict[str, str]:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        return {
            "status": "stub",
            "message": "Telegram bot token not set. Set TELEGRAM_BOT_TOKEN to enable.",
        }

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests.post(url, json=payload, timeout=10)
    if resp.ok:
        return {"status": "sent", "telegram_response": resp.json()}
    return {"status": "error", "error": resp.text}
