# Voice-Based Email & Messaging Assistant

## Overview
Open-source assistant that accepts voice commands to send/read emails and messages, and reads content out loud.

## Phases
- Phase 1: scaffold + baseline APIs
- Phase 2: voice pipeline, email integration, summarization
- Phase 3: messaging bots, dashboard, multi-language
- Phase 4: tests, CI, Docker, deployment

## Quick start
1. Create venv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run app:

```powershell
set FLASK_APP=src.app
set FLASK_ENV=development
set GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/auth/google/callback
flask run
```

4. Health check:

```powershell
curl http://127.0.0.1:5000/health
```

## Structure
- `src/`: source code
- `test/`: tests
- `docs/`: design and phase docs
- `.github/`: CI and instructions

## API Endpoints (Phase 2)
- `GET /health`
- `POST /voice/transcribe`  (multipart `audio`)
- `POST /voice/speak`  (JSON `{ "text": "..." }`)
- `POST /email/send`  (JSON `{ "to", "subject", "body" }`)
- `GET /email/status`
- `GET /email/list` (stub)
- `GET /email/read/<message_id>` (stub)
- `POST /nlp/summarize`  (JSON `{ "text": "..." }`)
- `POST /nlp/suggest`  (JSON `{ "text": "..." }`)
- `POST /message/telegram`  (JSON `{ "chat_id", "text" }`)

## Environment Variables
- `DATABASE_URL` (default `sqlite:///./data.db`)
- `GMAIL_API_ENABLED=false`
- `GOOGLE_OAUTH_CREDENTIALS_PATH=.secrets/google_oauth.json`
- `GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/auth/google/callback`
- `TELEGRAM_BOT_TOKEN` (optional)
- `NLP_MODEL=google/flan-t5-small`

## Google OAuth Setup
For Gmail login, create a Google OAuth Web application and make sure the authorized redirect URI exactly matches:

- `http://localhost:5000/auth/google/callback`

If you later run the app on `127.0.0.1`, add this separately in Google Cloud Console:

- `http://127.0.0.1:5000/auth/google/callback`

## Contributing
- Use feature branches
- Format with `black`, lint with `ruff`
- Add tests for each behavior
