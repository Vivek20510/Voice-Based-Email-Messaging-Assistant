import os
from typing import Dict

from src.services.auth import get_token, register_token
from src.services.gmail_service import (
    send_email_real,
    fetch_message_summaries,
    fetch_message,
)


def send_email(to: str, subject: str, body: str, user_id: int = None) -> Dict[str, str]:
    """Send an email via Gmail API or stub on missing config."""
    if os.getenv("GMAIL_API_ENABLED", "false").lower() not in ["1", "true", "yes"]:
        return {
            "status": "stub",
            "message": "Email sending stubbed. Set GMAIL_API_ENABLED=true to enable real integration.",
            "to": to,
            "subject": subject,
            "body": body,
        }

    if not user_id:
        return {"status": "error", "message": "Gmail send requires a signed-in user."}

    token = get_token(user_id, "gmail")
    if not token:
        return {
            "status": "error",
            "message": "No Gmail credentials available for the signed-in user.",
        }

    return send_email_real(to, subject, body, token, user_id, register_token)


def list_emails(user_id: int):
    if os.getenv("GMAIL_API_ENABLED", "false").lower() not in ["1", "true", "yes"]:
        return {"status": "stub", "messages": [], "emails": []}

    if not user_id:
        return {"status": "error", "message": "Authentication required."}

    token = get_token(user_id, "gmail")
    if not token:
        return {
            "status": "error",
            "message": "No Gmail credentials available for the signed-in user.",
        }

    messages = fetch_message_summaries(token, user_id, register_token)
    return {"status": "ok", "messages": messages, "emails": messages}


def read_email(user_id: int, message_id: str):
    if os.getenv("GMAIL_API_ENABLED", "false").lower() not in ["1", "true", "yes"]:
        return {
            "status": "stub",
            "message_id": message_id,
            "body": "This is a placeholder.",
        }

    if not user_id:
        return {"status": "error", "message": "Authentication required."}

    token = get_token(user_id, "gmail")
    if not token:
        return {
            "status": "error",
            "message": "No Gmail credentials available for the signed-in user.",
        }

    email = fetch_message(token, user_id, register_token, message_id)
    return {"status": "ok", "message": email}
