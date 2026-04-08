from types import SimpleNamespace

from src.app import app


def test_auth_login_uses_configured_redirect_uri(monkeypatch):
    client = app.test_client()
    monkeypatch.setenv(
        "GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:5000/auth/google/callback"
    )

    captured = {}

    def fake_get_validated_redirect_uri(fallback_uri):
        captured["fallback_uri"] = fallback_uri
        return "http://localhost:5000/auth/google/callback"

    def fake_get_authorization_url(redirect_uri):
        captured["redirect_uri"] = redirect_uri
        return "https://accounts.google.com/mock", "state-123", "verifier-123"

    monkeypatch.setattr(
        "src.web.auth_routes.get_validated_redirect_uri",
        fake_get_validated_redirect_uri,
    )
    monkeypatch.setattr(
        "src.web.auth_routes.get_authorization_url", fake_get_authorization_url
    )

    response = client.get("/auth/login-oauth")

    assert response.status_code == 302
    assert response.headers["Location"] == "https://accounts.google.com/mock"
    assert captured["redirect_uri"] == "http://localhost:5000/auth/google/callback"
    assert captured["fallback_uri"].endswith("/auth/google/callback")
    with client.session_transaction() as session:
        assert session["oauth_state"] == "state-123"
        assert session["oauth_code_verifier"] == "verifier-123"


def test_auth_login_renders_mismatch_error(monkeypatch):
    client = app.test_client()
    monkeypatch.setattr(
        "src.web.auth_routes.get_validated_redirect_uri",
        lambda fallback_uri: (_ for _ in ()).throw(
            RuntimeError(
                "Configured redirect URI does not match Google OAuth client settings."
            )
        ),
    )

    response = client.get("/auth/login-oauth")

    assert response.status_code == 200
    assert (
        b"Configured redirect URI does not match Google OAuth client settings."
        in response.data
    )


def test_auth_login_falls_back_to_request_url_when_env_missing(monkeypatch):
    client = app.test_client()
    monkeypatch.delenv("GOOGLE_OAUTH_REDIRECT_URI", raising=False)

    captured = {}

    def fake_get_validated_redirect_uri(fallback_uri):
        captured["redirect_uri"] = fallback_uri
        return fallback_uri

    monkeypatch.setattr(
        "src.web.auth_routes.get_validated_redirect_uri",
        fake_get_validated_redirect_uri,
    )
    monkeypatch.setattr(
        "src.web.auth_routes.get_authorization_url",
        lambda redirect_uri: ("https://accounts.google.com/mock", "state-123", "verifier-123"),
    )

    response = client.get("/auth/login-oauth", base_url="http://localhost:5000")

    assert response.status_code == 302
    assert captured["redirect_uri"] == "http://localhost:5000/auth/google/callback"


def test_auth_callback_uses_same_redirect_uri_for_token_exchange(monkeypatch):
    client = app.test_client()
    monkeypatch.setenv(
        "GOOGLE_OAUTH_REDIRECT_URI", "http://localhost:5000/auth/google/callback"
    )

    with client.session_transaction() as session:
        session["oauth_state"] = "state-123"
        session["oauth_code_verifier"] = "verifier-123"

    captured = {}

    monkeypatch.setattr(
        "src.web.auth_routes.get_validated_redirect_uri",
        lambda fallback_uri: "http://localhost:5000/auth/google/callback",
    )

    def fake_exchange_authorization_response_for_credentials(
        authorization_response, redirect_uri, code_verifier
    ):
        captured["authorization_response"] = authorization_response
        captured["redirect_uri"] = redirect_uri
        captured["code_verifier"] = code_verifier
        return SimpleNamespace(
            token="token-123", refresh_token="refresh-123", expiry=None
        )

    monkeypatch.setattr(
        "src.web.auth_routes.exchange_authorization_response_for_credentials",
        fake_exchange_authorization_response_for_credentials,
    )
    monkeypatch.setattr(
        "src.web.auth_routes._fetch_user_email", lambda access_token: "test@example.com"
    )
    monkeypatch.setattr(
        "src.web.auth_routes.register_token", lambda *args, **kwargs: {"status": "ok"}
    )

    fake_user = SimpleNamespace(
        id=1, email="test@example.com", name="test", hashed_password=""
    )

    class FakeQuery:
        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return fake_user

    class FakeDb:
        def query(self, model):
            return FakeQuery()

        def add(self, obj):
            pass

        def commit(self):
            pass

        def refresh(self, obj):
            pass

        def close(self):
            pass

    monkeypatch.setattr("src.web.auth_routes.get_db", lambda: iter([FakeDb()]))

    response = client.get(
        "/auth/google/callback?state=state-123&code=auth-code",
        base_url="http://localhost:5000",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    assert captured == {
        "authorization_response": "http://localhost:5000/auth/google/callback?state=state-123&code=auth-code",
        "code_verifier": "verifier-123",
        "redirect_uri": "http://localhost:5000/auth/google/callback",
    }


def test_auth_callback_renders_exact_token_exchange_error(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["oauth_state"] = "state-123"
        session["oauth_code_verifier"] = "verifier-123"

    monkeypatch.setattr(
        "src.web.auth_routes.get_validated_redirect_uri",
        lambda fallback_uri: "http://localhost:5000/auth/google/callback",
    )
    monkeypatch.setattr(
        "src.web.auth_routes.exchange_authorization_response_for_credentials",
        lambda authorization_response, redirect_uri, code_verifier: (_ for _ in ()).throw(
            RuntimeError("invalid_grant: Bad Request")
        ),
    )

    response = client.get(
        "/auth/google/callback?state=state-123&code=auth-code",
        base_url="http://localhost:5000",
    )

    assert response.status_code == 500
    assert b"OAuth token exchange failed: invalid_grant: Bad Request" in response.data


def test_auth_callback_requires_code_verifier(monkeypatch):
    client = app.test_client()

    with client.session_transaction() as session:
        session["oauth_state"] = "state-123"

    monkeypatch.setattr(
        "src.web.auth_routes.get_validated_redirect_uri",
        lambda fallback_uri: "http://localhost:5000/auth/google/callback",
    )

    response = client.get(
        "/auth/google/callback?state=state-123&code=auth-code",
        base_url="http://localhost:5000",
    )

    assert response.status_code == 500
    assert (
        b"OAuth token exchange failed: Missing OAuth code verifier. Start the Google login flow again."
        in response.data
    )
