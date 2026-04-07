from typing import Dict, Any
import os

import requests

from src.services.nlp_service import summarize_text


TELEGRAM_API_URL = "https://api.telegram.org"


def _bot_token():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")
    return token


def send_message(chat_id: str, text: str, reply_markup: Dict[str, Any] = None) -> Dict[str, Any]:
    token = _bot_token()
    url = f"{TELEGRAM_API_URL}/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup is not None:
        payload["reply_markup"] = reply_markup
    resp = requests.post(url, json=payload, timeout=10)
    if resp.ok:
        return {"status": "sent", "result": resp.json()}
    return {"status": "error", "error": resp.text}


def handle_command(chat_id: str, text: str) -> str:
    normalized = text.strip().lower()
    if normalized.startswith("/start"):
        return (
            "Welcome! I can help you send and read emails via voice and Telegram.\n"
            "Use /help to see commands."
        )
    if normalized.startswith("/help"):
        return (
            "Available commands:\n"
            "/start - Start the assistant\n"
            "/help - Show this help message\n"
            "/email_list - List latest emails (requires Gmail login)\n"
            "/email_read <id> - Read a specific email\n"
            "/summarize <text> - Summarize text\n"
            "/echo <text> - Echo back the text"
        )
    if normalized.startswith("/email_list"):
        return "Email list feature is not configured for Telegram yet. Please use the web app after login."
    if normalized.startswith("/email_read"):
        return "Email read feature is not configured for Telegram yet. Please use the web app after login."
    if normalized.startswith("/summarize"):
        payload = text.partition(" ")[2].strip()
        if not payload:
            return "Provide text after /summarize to summarize."
        try:
            result = summarize_text(payload)
            summary = result.get("summary", "No summary available")
            return f"Summary:\n{summary}"
        except Exception as exc:
            return f"Unable to summarize text: {exc}"
    if normalized.startswith("/echo"):
        payload = text.partition(" ")[2].strip()
        return payload or "Send /echo followed by text to echo it back."
    return (
        "I didn't understand that command. Use /help to see available commands."
    )


def handle_update(update: Dict[str, Any]) -> Dict[str, Any]:
    message = update.get("message") or update.get("edited_message")
    if not message:
        return {"status": "ignored", "reason": "no message found"}

    chat = message.get("chat", {})
    chat_id = str(chat.get("id"))
    text = message.get("text", "")
    if not text:
        return {"status": "ignored", "reason": "no text message"}

    response_text = handle_command(chat_id, text)
    return send_message(chat_id, response_text)
