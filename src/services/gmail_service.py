import os
import json
import base64
from email.mime.text import MIMEText
from datetime import datetime

import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def resolve_redirect_uri(fallback_uri: str = None):
    redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI") or fallback_uri
    if not redirect_uri:
        raise RuntimeError("GOOGLE_OAUTH_REDIRECT_URI is not configured")
    return redirect_uri


def _credentials_file_path():
    path = os.getenv("GOOGLE_OAUTH_CREDENTIALS_PATH")
    if not path:
        raise RuntimeError("GOOGLE_OAUTH_CREDENTIALS_PATH is not configured")
    if not os.path.exists(path):
        raise RuntimeError(f"Google OAuth credentials file not found at {path}")
    return path


def create_oauth_flow(redirect_uri: str):
    return Flow.from_client_secrets_file(
        _credentials_file_path(),
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )


def get_authorization_url(redirect_uri: str):
    flow = create_oauth_flow(redirect_uri)
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return auth_url, state, flow.code_verifier


def exchange_code_for_credentials(code: str, redirect_uri: str):
    flow = create_oauth_flow(redirect_uri)
    flow.fetch_token(code=code)
    return flow.credentials


def exchange_authorization_response_for_credentials(
    authorization_response: str, redirect_uri: str, code_verifier: str = None
):
    flow = create_oauth_flow(redirect_uri)
    if code_verifier:
        flow.code_verifier = code_verifier
    flow.fetch_token(authorization_response=authorization_response)
    return flow.credentials


def _load_client_config():
    path = _credentials_file_path()
    with open(path, "r", encoding="utf-8") as handle:
        client_config = json.load(handle)
    if "web" in client_config:
        return client_config["web"]
    if "installed" in client_config:
        return client_config["installed"]
    raise RuntimeError(
        "Google OAuth credentials file must contain a 'web' or 'installed' entry."
    )


def validate_redirect_uri(redirect_uri: str):
    config = _load_client_config()
    allowed_redirect_uris = config.get("redirect_uris", [])
    if redirect_uri not in allowed_redirect_uris:
        raise RuntimeError(
            "Configured redirect URI does not match Google OAuth client settings."
        )
    return redirect_uri


def get_validated_redirect_uri(fallback_uri: str = None):
    redirect_uri = resolve_redirect_uri(fallback_uri)
    return validate_redirect_uri(redirect_uri)


def _build_credentials_from_token(user_token):
    config = _load_client_config()
    return Credentials(
        token=user_token.access_token,
        refresh_token=user_token.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.get("client_id"),
        client_secret=config.get("client_secret"),
        scopes=SCOPES,
    )


def _ensure_valid_credentials(user_token, user_id, register_token_fn):
    creds = _build_credentials_from_token(user_token)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        expires_in = (
            int((creds.expiry - datetime.utcnow()).total_seconds())
            if creds.expiry
            else None
        )
        register_token_fn(
            user_id, "gmail", creds.token, creds.refresh_token, expires_in
        )
    return creds


def build_gmail_service(user_token, user_id, register_token_fn):
    creds = _ensure_valid_credentials(user_token, user_id, register_token_fn)
    return build("gmail", "v1", credentials=creds), creds


def _create_message(sender: str, to: str, subject: str, body: str):
    message = MIMEText(body)
    message["to"] = to
    message["from"] = sender
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw}


def send_email_real(
    to: str, subject: str, body: str, user_token, user_id, register_token_fn
):
    gmail_service, _ = build_gmail_service(user_token, user_id, register_token_fn)
    message_body = _create_message("me", to, subject, body)
    sent = (
        gmail_service.users().messages().send(userId="me", body=message_body).execute()
    )
    return {"status": "sent", "message_id": sent.get("id"), "gmail_response": sent}


def fetch_message_ids(user_token, user_id, register_token_fn, max_results: int = 10):
    gmail_service, _ = build_gmail_service(user_token, user_id, register_token_fn)
    results = (
        gmail_service.users()
        .messages()
        .list(userId="me", maxResults=max_results)
        .execute()
    )
    return results.get("messages", [])


def fetch_message(user_token, user_id, register_token_fn, message_id: str):
    gmail_service, _ = build_gmail_service(user_token, user_id, register_token_fn)
    message = (
        gmail_service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    payload = message.get("payload", {})
    headers = payload.get("headers", [])
    snippet = message.get("snippet")
    parts = payload.get("parts", [])
    body = ""
    if parts:
        for part in parts:
            if part.get("mimeType") == "text/plain" and part.get("body", {}).get(
                "data"
            ):
                body = base64.urlsafe_b64decode(part["body"]["data"].encode()).decode(
                    "utf-8", errors="ignore"
                )
                break
    return {
        "id": message.get("id"),
        "snippet": snippet,
        "subject": next(
            (h.get("value") for h in headers if h.get("name") == "Subject"), ""
        ),
        "from": next((h.get("value") for h in headers if h.get("name") == "From"), ""),
        "body": body,
    }


def get_user_email_from_token(creds):
    url = "https://openidconnect.googleapis.com/v1/userinfo"
    response = requests.get(
        url, headers={"Authorization": f"Bearer {creds.token}"}, timeout=10
    )
    response.raise_for_status()
    return response.json().get("email")
