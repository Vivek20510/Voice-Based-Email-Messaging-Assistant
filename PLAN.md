# Voice-Based Email & Messaging Assistant — Complete Multi-Phase Plan

## Overview
Open-source voice assistant for email and messaging with a Python/Flask backend and an HTML/CSS/JS frontend. Uses Whisper for transcription, pyttsx3/gTTS for TTS, HuggingFace transformers for NLP, Gmail OAuth for email, and Telegram Bot API for messaging. Deployable to free cloud tiers like Railway or Render.

**Current Status:** Phase 3.6 complete ✅, Phase 3.6.2 (frontend improvements) in progress 🔄

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

## Phase 3: Real Integrations + Multi-Language + Frontend ✅ COMPLETE

### Phase 3.1-3.5: Gmail OAuth, Telegram, Multi-Language, Frontend, Testing ✅ COMPLETE

#### Objectives
- Implement Gmail OAuth 2.0 login flow with database token storage
- Add Telegram webhook and messaging support
- Enable multi-language voice transcription and TTS
- Build vanilla HTML/CSS/JS frontend with login, dashboard, settings
- Add comprehensive testing with CI coverage

#### Deliverables
- `src/services/gmail_service.py`, `src/web/auth_routes.py`
- `src/web/telegram_routes.py`, `src/services/telegram_service.py`
- Enhanced `src/services/voice.py` with language detection
- Frontend templates: `base.html`, `login.html`, `signup.html`, `dashboard.html`, `settings.html`
- Static assets: `static/css/style.css`, `static/js/app.js`, `static/js/api.js`, `static/js/audio.js`
- Test files: `test/test_auth_phase3_6.py`, `test/test_messaging_service_user_tokens.py`
- Documentation: `docs/SETUP_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/API_REFERENCE.md`, `docs/DEPLOYMENT.md`

#### Outcome
Fully functional backend with real Gmail and Telegram integrations, multi-language voice support, and a basic frontend with authentication and settings.

### Phase 3.6: SQLite Auth, Settings-Driven Services, Voicemail Dashboard ✅ COMPLETE

#### Objectives
- Implement SQLite-backed authentication with email/password and OAuth
- Add settings page for Gmail and Telegram service connections
- Create voicemail-style dashboard with service status indicators
- Enable user-specific token storage for services

#### Deliverables
- Enhanced `src/web/auth_routes.py` with login/signup/OAuth/settings routes
- `src/models.py` with User and UserToken models
- Updated `src/services/messaging_service.py` for user-token lookup
- Voicemail dashboard template with service status display
- Settings page with Gmail OAuth and Telegram token entry

#### Outcome
Complete authentication system with persistent service connections and a functional voicemail-style inbox dashboard.

### Phase 3.6.2: Frontend Prototype Matching 🔄 IN PROGRESS

#### Objectives
- Enhance frontend to fully match voicemail prototype features
- Add compose page with voice dictation and service selection
- Implement message view modal with reply functionality
- Improve dashboard interactions and UI polish

#### Deliverables
- `templates/compose.html` with voice dictation and service selection
- Enhanced `templates/dashboard.html` with message view modal
- Updated `static/js/app.js` for modal and compose interactions
- Header navigation updates in `templates/base.html`

#### Known Issues
- Test suite has fixture conflicts (shared DB across tests); handle as separate task
- Frontend improvements needed to match full prototype (documented but not implemented yet)

#### Outcome
Frontend fully matches prototype with compose, message view, and voice features.

---

## Phase 4: Deployment & DevOps 🔄 NEXT

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
GOOGLE_OAUTH_CREDENTIALS_PATH=.secrets/client_secret_2_370325942201-lrhpk5nuofeqau9afflke2n7huqp7fqq.apps.googleusercontent.com.json
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/auth/google/callback
TELEGRAM_BOT_TOKEN=<token>
NLP_MODEL=google/flan-t5-small
TORCH_DEVICE=cpu
SENTRY_DSN=
LOG_LEVEL=INFO
```

---

## Notes
- Phase 1-3.6 completed.
- Phase 3.6.2 (frontend improvements) in progress to match prototype.
- Test suite has fixture conflicts (shared DB); handle separately.
- Frontend enhancements documented but not implemented yet.
- Phase 4 begins with containerization and deployment.

---

## Next Steps
1. Complete Phase 3.6.2: Enhance frontend to match full prototype features.
2. Fix test fixture conflicts for reliable CI.
3. Begin Phase 4: Containerize and deploy to Railway/Render.
4. Add monitoring and production optimizations.
