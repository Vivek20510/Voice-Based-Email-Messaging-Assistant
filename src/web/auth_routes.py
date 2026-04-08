import os
import datetime
from flask import (
    Blueprint,
    redirect,
    request,
    session,
    url_for,
    render_template,
    jsonify,
)
import requests

from src.db import SessionLocal
from src.models import User, UserToken
from src.services.gmail_service import (
    get_authorization_url,
    exchange_authorization_response_for_credentials,
    get_validated_redirect_uri,
)
from src.services.auth import register_token, hash_password, verify_password

auth_bp = Blueprint("auth", __name__)


def _get_service_status(user_id: int | None):
    """Get service connection status for the given user."""
    if not user_id:
        return {"gmail_connected": False, "telegram_connected": False}
    
    db = next(get_db())
    gmail_token = (
        db.query(UserToken)
        .filter(UserToken.user_id == user_id, UserToken.service == "gmail")
        .first()
    )
    telegram_token = (
        db.query(UserToken)
        .filter(UserToken.user_id == user_id, UserToken.service == "telegram")
        .first()
    )
    
    return {
        "gmail_connected": bool(gmail_token),
        "telegram_connected": bool(telegram_token),
    }


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@auth_bp.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    if request.method == "GET":
        return render_template("login.html")

    # POST: Email/password login
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()

    if not email or not password:
        return render_template("login.html", error="Email and password required"), 400

    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()

    if (
        not user
        or not user.hashed_password
        or not verify_password(password, user.hashed_password)
    ):
        return render_template("login.html", error="Invalid email or password"), 401

    session["user_id"] = user.id
    session["user_email"] = user.email
    return redirect(url_for("auth.dashboard"))


@auth_bp.route("/auth/signup", methods=["GET", "POST"])
def auth_signup():
    if request.method == "GET":
        return render_template("signup.html")

    # POST: Email/password signup
    email = request.form.get("email", "").strip()
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "").strip()
    confirm_password = request.form.get("confirm_password", "").strip()

    if not email or not name or not password:
        return render_template("signup.html", error="All fields required"), 400

    if password != confirm_password:
        return render_template("signup.html", error="Passwords do not match"), 400

    if len(password) < 6:
        return (
            render_template(
                "signup.html", error="Password must be at least 6 characters"
            ),
            400,
        )

    db = next(get_db())
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return render_template("signup.html", error="Email already registered"), 409

    hashed_pwd = hash_password(password)
    user = User(email=email, name=name, hashed_password=hashed_pwd)
    db.add(user)
    db.commit()
    db.refresh(user)

    session["user_id"] = user.id
    session["user_email"] = user.email
    return redirect(url_for("auth.dashboard"))


@auth_bp.route("/auth/login-oauth")
def auth_login_oauth():
    next_url = request.args.get("next", "dashboard")
    redirect_uri = url_for("auth.auth_callback", _external=True)
    try:
        redirect_uri = get_validated_redirect_uri(redirect_uri)
        auth_url, state, code_verifier = get_authorization_url(redirect_uri)
    except RuntimeError as exc:
        return render_template("login.html", oauth_error=str(exc))
    session["oauth_state"] = state
    session["oauth_code_verifier"] = code_verifier
    session["oauth_next"] = next_url
    return redirect(auth_url)


@auth_bp.route("/auth/google/callback")
def auth_callback():
    error = request.args.get("error")
    if error:
        return render_template("error.html", message=error), 400

    state = request.args.get("state")
    if not state or state != session.get("oauth_state"):
        return render_template("error.html", message="Invalid OAuth state."), 400

    code = request.args.get("code")
    if not code:
        return render_template("error.html", message="Missing authorization code."), 400

    redirect_uri = url_for("auth.auth_callback", _external=True)
    try:
        redirect_uri = get_validated_redirect_uri(redirect_uri)
        code_verifier = session.get("oauth_code_verifier")
        if not code_verifier:
            raise RuntimeError(
                "Missing OAuth code verifier. Start the Google login flow again."
            )
        credentials = exchange_authorization_response_for_credentials(
            request.url, redirect_uri, code_verifier
        )
    except Exception as exc:
        print(f"OAuth token exchange failed: {exc}")
        return (
            render_template("error.html", message=f"OAuth token exchange failed: {exc}"),
            500,
        )

    email = _fetch_user_email(credentials.token)
    if not email:
        return (
            render_template(
                "error.html", message="Failed to retrieve email from Google."
            ),
            500,
        )

    db = next(get_db())
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, name=email.split("@")[0], hashed_password="")
        db.add(user)
        db.commit()
        db.refresh(user)

    expires_in = (
        int((credentials.expiry - datetime.datetime.utcnow()).total_seconds())
        if credentials.expiry
        else None
    )
    register_token(
        user.id, "gmail", credentials.token, credentials.refresh_token, expires_in
    )

    session.pop("oauth_code_verifier", None)
    session.pop("oauth_state", None)
    session["user_id"] = user.id
    session["user_email"] = user.email
    next_url = session.pop("oauth_next", "dashboard")
    if next_url == "settings":
        return redirect(url_for("auth.settings"))
    return redirect(url_for("auth.dashboard"))


@auth_bp.route("/auth/logout")
def auth_logout():
    session.clear()
    return redirect(url_for("home"))


@auth_bp.route("/auth/status")
def auth_status():
    user_id = session.get("user_id")
    service_status = _get_service_status(user_id)
    return jsonify(
        {
            "authenticated": bool(session.get("user_email")),
            "user_email": session.get("user_email"),
            "gmail_enabled": os.getenv("GMAIL_API_ENABLED", "false").lower()
            in ["true", "1", "yes"],
            **service_status,
        }
    )


@auth_bp.route("/dashboard")
def dashboard():
    if not session.get("user_email"):
        return redirect(url_for("auth.auth_login"))
    user_id = session.get("user_id")
    service_status = _get_service_status(user_id)
    return render_template(
        "dashboard.html",
        user_email=session.get("user_email"),
        **service_status,
    )


def _fetch_user_email(access_token: str):
    url = "https://openidconnect.googleapis.com/v1/userinfo"
    response = requests.get(
        url, headers={"Authorization": f"Bearer {access_token}"}, timeout=10
    )
    if response.ok:
        return response.json().get("email")
    return None


@auth_bp.route("/settings")
def settings():
    """Settings page for service connections."""
    if not session.get("user_email"):
        return redirect(url_for("auth.auth_login"))
    user_id = session.get("user_id")
    service_status = _get_service_status(user_id)
    return render_template(
        "settings.html",
        user_email=session.get("user_email"),
        **service_status,
    )


@auth_bp.route("/settings/gmail/connect")
def settings_gmail_connect():
    """Initiate Gmail OAuth connection from settings."""
    if not session.get("user_email"):
        return redirect(url_for("auth.auth_login"))
    
    next_url = "settings"
    redirect_uri = url_for("auth.auth_callback", _external=True)
    try:
        redirect_uri = get_validated_redirect_uri(redirect_uri)
        auth_url, state, code_verifier = get_authorization_url(redirect_uri)
    except RuntimeError as exc:
        return render_template("settings.html", error="Gmail setup failed: " + str(exc)), 400
    
    session["oauth_state"] = state
    session["oauth_code_verifier"] = code_verifier
    session["oauth_next"] = next_url
    return redirect(auth_url)


@auth_bp.route("/settings/telegram", methods=["POST"])
def settings_telegram():
    """Store Telegram bot token."""
    if not session.get("user_email"):
        return redirect(url_for("auth.auth_login"))
    
    telegram_token = request.form.get("telegram_token", "").strip()
    if not telegram_token:
        service_status = _get_service_status(session.get("user_id"))
        return render_template(
            "settings.html",
            user_email=session.get("user_email"),
            error="Telegram bot token cannot be empty",
            **service_status,
        ), 400
    
    user_id = session.get("user_id")
    db = next(get_db())
    
    # Check if token already exists
    existing_token = (
        db.query(UserToken)
        .filter(UserToken.user_id == user_id, UserToken.service == "telegram")
        .first()
    )
    
    if existing_token:
        # Update existing token
        existing_token.access_token = telegram_token
        existing_token.expires_at = datetime.datetime.utcnow()
    else:
        # Create new token
        token = UserToken(
            user_id=user_id,
            service="telegram",
            access_token=telegram_token,
            refresh_token=None,
            expires_at=datetime.datetime.utcnow(),
        )
        db.add(token)
    
    db.commit()
    
    service_status = _get_service_status(user_id)
    return render_template(
        "settings.html",
        user_email=session.get("user_email"),
        success="Telegram bot token saved successfully",
        **service_status,
    )
