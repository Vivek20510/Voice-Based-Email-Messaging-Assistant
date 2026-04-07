# Voice-Based Email & Messaging Assistant — Complete Multi-Phase Plan

## Overview
Open-source voice assistant for email and messaging with a Python/Flask backend and an HTML/CSS/JS frontend. Uses Whisper for transcription, pyttsx3/gTTS for TTS, HuggingFace transformers for NLP, Gmail OAuth for email, and Telegram Bot API for messaging. Deployable to free cloud tiers like Railway or Render.

**Current Status:** Phase 1-2 complete ✅

---

## Phase 1: Foundation & Scaffolding ✅ COMPLETE

### Objectives
- Build project scaffolding and developer workflow
- Set up Flask backend, SQLite database, and CI
- Create baseline documentation and project conventions

### Deliverables
- `src/`, `test/`, `docs/`, `.github/`
- `requirements.txt`
- `README.md`
- GitHub Actions workflow
- `src/app.py` with health endpoint
- `.github/copilot-instructions.md`
- `.gitignore`
- `test/test_app.py`

### Outcome
A functioning Python Flask project with core backend scaffolding and unit test coverage.

---

## Phase 2: Core APIs (Voice + Email Stubs + NLP) ✅ COMPLETE

### Objectives
- Add voice transcription and speech output
- Add email service stubs with OAuth hooks
- Add NLP endpoints for summarization and suggested replies
- Add Telegram messaging stubs

### Deliverables
- `src/services/voice.py`
- `src/services/email_service.py`
- `src/services/nlp_service.py`
- `src/services/messaging_service.py`
- `src/services/auth.py`
- `src/models.py` with user and token models
- API routes for voice, email, NLP, and Telegram
- Expanded tests and CI workflow

### Outcome
A capable backend API with stubbed integrations and automated test validation.

---

## Phase 3: Real Integrations + Multi-Language + Frontend 🔄 IN PROGRESS

### Phase 3.1: Gmail OAuth Integration (Backend)

#### Objectives
- Implement Gmail OAuth 2.0 login flow
- Store Gmail tokens in the database
- Enable real Gmail send/read operations through the API

#### User Setup Tasks
1. Create a Google Cloud project.
2. Enable Gmail API.
3. Create OAuth 2.0 credentials for a Web application.
4. Add redirect URI for local development:
   - `http://localhost:5000/auth/google/callback`
5. Download credentials JSON and save as `.secrets/google_oauth.json`.
6. Set environment variables in `.env`:
   - `GMAIL_API_ENABLED=true`
   - `GOOGLE_OAUTH_CREDENTIALS_PATH=.secrets/google_oauth.json`
   - `GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/auth/google/callback`

#### Backend Tasks
- Create `src/services/gmail_service.py`
- Create `src/web/auth_routes.py`
- Create `templates/login.html`, `templates/base.html` and a placeholder `templates/dashboard.html`
- Add session support in `src/app.py`
- Update `src/services/auth.py` with token management helpers
- Add OAuth credentials path to `.gitignore`
- Update `requirements.txt`

#### Test Coverage
- `test/test_gmail_service.py`
- `test/test_auth_routes.py`

---

### Phase 3.2: Telegram Webhook + Conversational Commands

#### Objectives
- Add Telegram webhook support
- Process incoming messages and commands
- Maintain conversation state for multi-turn interactions

#### User Setup Tasks
1. Create a Telegram bot with BotFather.
2. Save the token to `.env`: `TELEGRAM_BOT_TOKEN=<token>`.
3. Configure webhook for production once deployed.

#### Backend Tasks
- Create `src/web/telegram_routes.py`
- Create `src/services/telegram_service.py`
- Add `Conversation` model to `src/models.py`
- Implement command handlers for `/start`, `/help`, `/email`, `/summarize`, `/reply`
- Add Telegram webhook route to `src/app.py`

#### Tests
- `test/test_telegram_routes.py`
- `test/test_telegram_service.py`

---

### Phase 3.3: Multi-Language Voice Support

#### Objectives
- Detect voice/text language automatically
- Speak text in the appropriate language
- Propagate language through NLP responses

#### Backend Tasks
- Add `langdetect` to `requirements.txt`
- Add `gTTS` to `requirements.txt`
- Extend `src/services/voice.py` for language detection
- Extend `src/services/nlp_service.py` with language-aware calls
- Update API responses with language metadata

#### Tests
- `test/test_voice_multilang.py`

---

### Phase 3.4: HTML/CSS/JS Frontend

#### Objectives
- Build a lightweight vanilla frontend
- Support login, voice upload, inbox view, compose, and Telegram help
- Use Web Audio API for browser voice capture

#### Frontend Structure
- `templates/base.html`
- `templates/index.html`
- `templates/login.html`
- `templates/dashboard.html`
- `templates/error.html`
- `static/css/style.css`
- `static/js/app.js`
- `static/js/audio.js`
- `static/js/api.js`

#### Tasks
- Render login and dashboard pages from Flask
- Implement voice recording and upload
- Implement email compose form and inbox listing
- Add settings and session checks

---

### Phase 3.5: Comprehensive Testing

#### Objectives
- Full unit and integration coverage
- Mock external APIs: Gmail, Telegram, HuggingFace
- Enforce coverage in CI

#### Test Files
- `test/test_gmail_service.py`
- `test/test_auth_routes.py`
- `test/test_telegram_routes.py`
- `test/test_telegram_service.py`
- `test/test_voice_multilang.py`
- `test/test_frontend_rendering.py`

#### CI
- Update `.github/workflows/python-app.yml`
- Add coverage and threshold

---

### Phase 3.6: Documentation

#### Files
- `docs/SETUP_GUIDE.md`
- `docs/ARCHITECTURE.md`
- `docs/API_REFERENCE.md`
- `docs/DEPLOYMENT.md`
- Update `README.md`

---

## Phase 4: Deployment & DevOps

### Phase 4.1: Containerization
- Create `Dockerfile`
- Create `docker-compose.yaml`
- Create `.dockerignore`

### Phase 4.2: Free Cloud Deployment
- Deploy to Railway or Render
- Configure env vars and OAuth redirect
- Update Telegram webhook URL

### Phase 4.3: Monitoring
- Add logging
- Optional Sentry integration

---

## Phase 5: Advanced Features

### Phase 5.1: WhatsApp Integration
- Add WhatsApp Cloud API support
- Implement webhook and messaging service

### Phase 5.2: Admin Dashboard
- Add admin UX for stats and message history

### Phase 5.3: Voice Intent/NLU
- Add command parsing and intent handling

### Phase 5.4: Desktop App
- Add Electron or PyQt native wrapper

---

## Environment Variables
```
FLASK_APP=src.app
FLASK_ENV=development
SECRET_KEY=replace-with-secret
DATABASE_URL=sqlite:///./data.db
GMAIL_API_ENABLED=true
GOOGLE_OAUTH_CREDENTIALS_PATH=.secrets/google_oauth.json
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/auth/google/callback
TELEGRAM_BOT_TOKEN=<token>
NLP_MODEL=google/flan-t5-small
TORCH_DEVICE=cpu
SENTRY_DSN=
LOG_LEVEL=INFO
```

---

## Notes
- Phase 1-2 completed.
- Phase 3 begins with Gmail OAuth.
- Frontend is vanilla HTML/CSS/JS.
- Deployment target: free cloud.

---

## Next Steps
1. Implement Gmail OAuth backend.
2. Add Telegram webhook support.
3. Add multi-language voice.
4. Build frontend.
5. Add full tests and deploy.
