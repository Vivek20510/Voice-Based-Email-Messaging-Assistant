import hashlib
import secrets
from typing import Dict
import datetime

from src.db import SessionLocal
from src.models import UserToken


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    """Hash a password with a salt."""
    salt = secrets.token_hex(32)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pwd_hash.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, pwd_hash = hashed.split('$')
        computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return computed_hash.hex() == pwd_hash
    except (AttributeError, TypeError, ValueError):
        return False


def register_token(user_id: int, service: str, access_token: str, refresh_token: str = None, expires_in: int = None) -> Dict[str, str]:
    db = next(get_db())
    expires_at = None
    if expires_in is not None:
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in)

    token = db.query(UserToken).filter(UserToken.user_id == user_id, UserToken.service == service).first()
    if not token:
        token = UserToken(user_id=user_id, service=service)

    token.access_token = access_token
    token.refresh_token = refresh_token
    token.expires_at = expires_at
    db.add(token)
    db.commit()

    return {"status": "ok", "message": "token saved"}


def get_token(user_id: int, service: str):
    db = next(get_db())
    token = db.query(UserToken).filter(UserToken.user_id == user_id, UserToken.service == service).first()
    if not token:
        return None
    return token
