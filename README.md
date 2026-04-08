# Voice-Based Email & Messaging Assistant

## Overview
Voice-Based Email & Messaging Assistant is a Flask-based web application that combines:

- voice transcription
- text-to-speech output
- Gmail OAuth and email APIs
- Telegram messaging and webhook handling
- NLP-powered summarization and reply suggestions
- a lightweight HTML/CSS/JS dashboard

The project is currently in an active prototype stage. The current implementation includes both backend APIs and a usable frontend, while the broader roadmap remains in [PLAN.md](/c:/Users/HP/Voice-Based%20Email%20%26%20Messaging%20Assistant/PLAN.md).

## Current Functionality

### Frontend
- Login page with email/password login
- Sign-up page with local account creation
- Google OAuth login entry point
- Dashboard for signed-in users
- Voice recording button that requests microphone access only when clicked
- Email compose form
- Inbox load/read actions wired to backend APIs
- Telegram status panel

### Backend
- `GET /health`
- `POST /voice/transcribe`
- `POST /voice/speak`
- `POST /email/send`
- `GET /email/status`
- `GET /email/list`
- `GET /email/read/<message_id>`
- `POST /nlp/summarize`
- `POST /nlp/suggest`
- `POST /message/telegram`
- `GET /auth/login`
- `POST /auth/login`
- `GET /auth/signup`
- `POST /auth/signup`
- `GET /auth/login-oauth`
- `GET /auth/google/callback`
- `GET /auth/logout`
- `GET /auth/status`
- `GET /dashboard`
- `POST /telegram/webhook`
- `GET /telegram/ping`

## Project Structure
- `src/` application code
- `src/services/` business logic for voice, email, Gmail OAuth, NLP, auth, and Telegram
- `src/web/` Flask blueprints for auth and Telegram webhook routes
- `templates/` frontend HTML templates
- `static/` frontend CSS and JavaScript
- `test/` automated tests
- `docs/` supporting docs
- `.github/` workflow and repo instructions

## Quick Start
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create your local environment file if needed:

```powershell
Copy-Item .env.example .env
```

4. Run the app:

```powershell
set FLASK_APP=src.app
set FLASK_ENV=development
flask run
```

5. Open the app:

```text
http://localhost:5000
```

6. Optional health check:

```powershell
curl http://localhost:5000/health
```

## Environment Variables

### Required for core app
- `SECRET_KEY`
- `DATABASE_URL`

### Required for Gmail OAuth / Gmail API
- `GMAIL_API_ENABLED`
- `GOOGLE_OAUTH_CREDENTIALS_PATH`
- `GOOGLE_OAUTH_REDIRECT_URI`

### Required for Telegram features
- `TELEGRAM_BOT_TOKEN`

### Optional
- `NLP_MODEL`

See [.env.example](/c:/Users/HP/Voice-Based%20Email%20%26%20Messaging%20Assistant/.env.example) for the expected format.

## Google OAuth Setup
To use Google sign-in and Gmail-backed email features:

1. Create a Google Cloud project.
2. Enable the Gmail API.
3. Create OAuth 2.0 credentials for a `Web application`.
4. Add this exact authorized redirect URI:

```text
http://localhost:5000/auth/google/callback
```

5. Download the credentials JSON and place it at:

```text
.secrets/google_oauth.json
```

6. Set these values in `.env`:

```text
GMAIL_API_ENABLED=true
GOOGLE_OAUTH_CREDENTIALS_PATH=.secrets/google_oauth.json
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/auth/google/callback
```

If you want to run the app on `127.0.0.1`, add that redirect URI separately in Google Cloud Console too.

## Notes About Current State
- Email/password auth is implemented locally.
- Google OAuth flow is implemented, but it depends on correct Google Cloud configuration.
- Gmail send/list/read logic exists, but real behavior depends on valid stored Gmail tokens.
- Voice transcription depends on Whisper being installed and working locally.
- Text-to-speech returns generated audio and includes a fallback path for restricted local environments.
- Telegram webhook handling and command parsing are implemented.
- The future roadmap is intentionally kept in `PLAN.md` and is not replaced by this README.

## Development
Run tests with:

```powershell
pytest -q
```

## Future Plan
The broader multi-phase roadmap remains unchanged in:

 [PLAN.md](/c:/Users/HP/Voice-Based%20Email%20%26%20Messaging%20Assistant/PLAN.md)
