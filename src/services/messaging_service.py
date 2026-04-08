import os
import requests
from typing import Dict, Optional

from src.db import SessionLocal
from src.models import UserToken


def send_telegram_message(
    chat_id: str, text: str, user_id: Optional[int] = None
) -> Dict[str, str]:
    """Send a Telegram message.
    
    Args:
        chat_id: The Telegram chat ID.
        text: The message text.
        user_id: Optional user ID to look up user-specific bot token.
    
    Returns:
        A response dictionary.
    """
    token = None
    
    # If user_id provided, look for user-specific token first
    if user_id:
        db = SessionLocal()
        try:
            user_token = (
                db.query(UserToken)
                .filter(
                    UserToken.user_id == user_id,
                    UserToken.service == "telegram",
                )
                .first()
            )
            if user_token:
                token = user_token.access_token
        finally:
            db.close()
    
    # Fall back to environment variable if no token found
    if not token:
        token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        return {
            "status": "stub",
            "message": "Telegram bot token not set. Set TELEGRAM_BOT_TOKEN env or add token in settings.",
        }

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    resp = requests.post(url, json=payload, timeout=10)
    if resp.ok:
        return {"status": "sent", "telegram_response": resp.json()}
    return {"status": "error", "error": resp.text}
