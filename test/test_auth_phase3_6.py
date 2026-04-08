"""Tests for Phase 3.6 authentication routes."""

import pytest
from src.app import app
from src.db import SessionLocal
from src.models import User, UserToken
from src.services.auth import hash_password


@pytest.fixture
def client():
    """Provide test client."""
    app.config['TESTING'] = True
    app.config['SESSION_COOKIE_SECURE'] = False
    with app.test_client() as client:
        yield client


@pytest.fixture
def db():
    """Provide database session."""
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=hash_password("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestLogin:
    def test_login_page_renders(self, client):
        """Test GET /auth/login returns login page."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data or b'login' in response.data

    def test_login_success(self, client, test_user):
        """Test successful email/password login."""
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=False)
        assert response.status_code == 302  # Redirect
        assert 'dashboard' in response.location

    def test_login_invalid_password(self, client, test_user):
        """Test login with wrong password."""
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        assert response.status_code == 401
        assert b'Invalid' in response.data or b'error' in response.data

    def test_login_nonexistent_email(self, client):
        """Test login with non-existent email."""
        response = client.post('/auth/login', data={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })
        assert response.status_code == 401

    def test_login_missing_email(self, client):
        """Test login with missing email."""
        response = client.post('/auth/login', data={
            'password': 'password123'
        })
        assert response.status_code == 400
        assert b'required' in response.data


class TestSignup:
    def test_signup_page_renders(self, client):
        """Test GET /auth/signup returns signup page."""
        response = client.get('/auth/signup')
        assert response.status_code == 200
        assert b'Sign' in response.data or b'sign' in response.data or b'Create' in response.data

    def test_signup_success(self, client, db):
        """Test successful signup."""
        response = client.post('/auth/signup', data={
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=False)
        assert response.status_code == 302
        assert 'dashboard' in response.location
        
        # Verify user was created
        user = db.query(User).filter(User.email == 'newuser@example.com').first()
        assert user is not None
        assert user.name == 'New User'

    def test_signup_password_mismatch(self, client):
        """Test signup with mismatched passwords."""
        response = client.post('/auth/signup', data={
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'password123',
            'confirm_password': 'password456'
        })
        assert response.status_code == 400
        assert b'match' in response.data or b'error' in response.data

    def test_signup_password_too_short(self, client):
        """Test signup with password < 6 characters."""
        response = client.post('/auth/signup', data={
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'short',
            'confirm_password': 'short'
        })
        assert response.status_code == 400
        assert b'6 character' in response.data or b'error' in response.data

    def test_signup_email_already_exists(self, client, test_user):
        """Test signup with email that already exists."""
        response = client.post('/auth/signup', data={
            'email': 'test@example.com',
            'name': 'Another User',
            'password': 'password123',
            'confirm_password': 'password123'
        })
        assert response.status_code == 409
        assert b'already' in response.data or b'registered' in response.data


class TestLogout:
    def test_logout(self, client, test_user):
        """Test logout clears session."""
        # Login first
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=False)
        assert response.status_code == 302
        assert 'home' in response.location or response.location == '/'


class TestAuthStatus:
    def test_auth_status_unauthenticated(self, client):
        """Test /auth/status for unauthenticated user."""
        response = client.get('/auth/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['authenticated'] is False

    def test_auth_status_authenticated(self, client, test_user):
        """Test /auth/status for authenticated user."""
        # Login
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/auth/status')
        assert response.status_code == 200
        data = response.get_json()
        assert data['authenticated'] is True
        assert data['user_email'] == 'test@example.com'
        assert 'gmail_connected' in data
        assert 'telegram_connected' in data


class TestSettings:
    def test_settings_page_requires_auth(self, client):
        """Test /settings requires authentication."""
        response = client.get('/settings', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location

    def test_settings_page_authenticated(self, client, test_user):
        """Test /settings renders for authenticated user."""
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/settings')
        assert response.status_code == 200
        assert b'Settings' in response.data or b'settings' in response.data

    def test_settings_telegram_submit(self, client, test_user, db):
        """Test submitting Telegram token."""
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.post('/settings/telegram', data={
            'telegram_token': '123456789:ABCxyz'
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert 'settings' in response.location
        
        # Verify token was saved
        token = db.query(UserToken).filter(
            UserToken.user_id == test_user.id,
            UserToken.service == 'telegram'
        ).first()
        assert token is not None
        assert token.access_token == '123456789:ABCxyz'

    def test_settings_telegram_empty_token(self, client, test_user):
        """Test submitting empty Telegram token."""
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.post('/settings/telegram', data={
            'telegram_token': ''
        })
        
        assert response.status_code == 400
        assert b'empty' in response.data or b'error' in response.data


class TestDashboard:
    def test_dashboard_requires_auth(self, client):
        """Test /dashboard requires authentication."""
        response = client.get('/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location

    def test_dashboard_authenticated(self, client, test_user):
        """Test /dashboard renders for authenticated user."""
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Voice' in response.data or b'dashboard' in response.data

    def test_dashboard_shows_service_status(self, client, test_user, db):
        """Test dashboard displays service connection status."""
        # Add Gmail token
        token = UserToken(
            user_id=test_user.id,
            service='gmail',
            access_token='dummy_token'
        )
        db.add(token)
        db.commit()
        
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        # Should show Gmail as connected
        assert b'Gmail' in response.data or b'gmail' in response.data


class TestGmailConnect:
    def test_gmail_connect_requires_auth(self, client):
        """Test /settings/gmail/connect requires authentication."""
        response = client.get('/settings/gmail/connect', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location

    def test_gmail_connect_authenticated(self, client, test_user):
        """Test /settings/gmail/connect authenticated."""
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/settings/gmail/connect', follow_redirects=False)
        # Should redirect to Google OAuth or error if credentials not available
        assert response.status_code in [302, 400]


class TestServiceStatus:
    def test_service_status_no_tokens(self, client, test_user):
        """Test service status when no tokens exist."""
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/auth/status')
        data = response.get_json()
        assert data['gmail_connected'] is False
        assert data['telegram_connected'] is False

    def test_service_status_with_gmail_token(self, client, test_user, db):
        """Test service status with Gmail token."""
        token = UserToken(
            user_id=test_user.id,
            service='gmail',
            access_token='dummy_token'
        )
        db.add(token)
        db.commit()
        
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/auth/status')
        data = response.get_json()
        assert data['gmail_connected'] is True
        assert data['telegram_connected'] is False

    def test_service_status_with_both_tokens(self, client, test_user, db):
        """Test service status with both tokens."""
        for service in ['gmail', 'telegram']:
            token = UserToken(
                user_id=test_user.id,
                service=service,
                access_token='dummy_token'
            )
            db.add(token)
        db.commit()
        
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        response = client.get('/auth/status')
        data = response.get_json()
        assert data['gmail_connected'] is True
        assert data['telegram_connected'] is True
