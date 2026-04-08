"""Tests for user-specific Telegram token lookup in messaging service."""

import pytest
import os
from unittest.mock import patch, MagicMock
from src.services.messaging_service import send_telegram_message
from src.db import SessionLocal
from src.models import User, UserToken
from src.services.auth import hash_password


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


class TestUserToken:
    @patch('src.services.messaging_service.requests.post')
    def test_send_with_user_token(self, mock_post, test_user, db):
        """Test sending Telegram message with user-specific token."""
        # Add user token
        token = UserToken(
            user_id=test_user.id,
            service='telegram',
            access_token='user_token_12345'
        )
        db.add(token)
        db.commit()
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {'ok': True, 'result': {'message_id': 1}}
        mock_post.return_value = mock_response
        
        # Send message
        result = send_telegram_message('12345', 'Test message', user_id=test_user.id)
        
        assert result['status'] == 'sent'
        # Verify it used the user token
        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert 'user_token_12345' in call_url

    @patch.dict(os.environ, {'TELEGRAM_BOT_TOKEN': 'env_token_67890'})
    @patch('src.services.messaging_service.requests.post')
    def test_send_with_env_token_fallback(self, mock_post):
        """Test fallback to environment token when no user token."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {'ok': True, 'result': {'message_id': 1}}
        mock_post.return_value = mock_response
        
        # Send message without user_id
        result = send_telegram_message('12345', 'Test message')
        
        assert result['status'] == 'sent'
        # Verify it used the env token
        call_url = mock_post.call_args[0][0]
        assert 'env_token_67890' in call_url

    @patch('src.services.messaging_service.requests.post')
    def test_send_with_user_token_overrides_env(self, mock_post, test_user, db):
        """Test user token takes precedence over env token."""
        # Set env token
        os.environ['TELEGRAM_BOT_TOKEN'] = 'env_token_67890'
        
        # Add user token
        token = UserToken(
            user_id=test_user.id,
            service='telegram',
            access_token='user_token_12345'
        )
        db.add(token)
        db.commit()
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {'ok': True, 'result': {'message_id': 1}}
        mock_post.return_value = mock_response
        
        # Send message
        result = send_telegram_message('12345', 'Test message', user_id=test_user.id)
        
        # Verify it used the user token, not env token
        call_url = mock_post.call_args[0][0]
        assert 'user_token_12345' in call_url
        assert 'env_token_67890' not in call_url
        
        # Cleanup
        del os.environ['TELEGRAM_BOT_TOKEN']

    def test_send_no_token_available(self):
        """Test sending without any token available."""
        # Make sure env var is not set
        if 'TELEGRAM_BOT_TOKEN' in os.environ:
            del os.environ['TELEGRAM_BOT_TOKEN']
        
        result = send_telegram_message('12345', 'Test message')
        
        assert result['status'] == 'stub'
        assert 'not set' in result['message'] or 'token' in result['message'].lower()

    @patch('src.services.messaging_service.requests.post')
    def test_send_error_response(self, mock_post, test_user, db):
        """Test handling of error response from Telegram API."""
        # Add user token
        token = UserToken(
            user_id=test_user.id,
            service='telegram',
            access_token='user_token_12345'
        )
        db.add(token)
        db.commit()
        
        # Mock error response
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.text = 'Unauthorized'
        mock_post.return_value = mock_response
        
        result = send_telegram_message('12345', 'Test message', user_id=test_user.id)
        
        assert result['status'] == 'error'
        assert result['error'] == 'Unauthorized'
