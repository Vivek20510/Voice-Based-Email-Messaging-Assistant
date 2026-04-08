# Voice-Based Email & Messaging Assistant — Architecture

## Project Overview

A Python/Flask backend with vanilla HTML/CSS/JS frontend for voice-based email and messaging.

**Tech Stack:**
- **Backend:** Python 3 + Flask + SQLAlchemy + SQLite
- **Voice:** Whisper (transcription) + gTTS (TTS)
- **NLP:** HuggingFace Transformers (summarization, suggestions)
- **Integrations:** Gmail OAuth, Telegram Bot API
- **Frontend:** Jinja2 templates + Vanilla JS + CSS

---

## Directory Structure

```
Voice-Based-Email-Messaging-Assistant/
├── src/
│   ├── app.py                      # Main Flask app
│   ├── db.py                       # SQLAlchemy session
│   ├── models.py                   # Database models
│   ├── services/
│   │   ├── auth.py                 # Password hashing, token mgmt
│   │   ├── voice.py                # Whisper + gTTS
│   │   ├── email_service.py        # Gmail API wrapper
│   │   ├── messaging_service.py    # Telegram API wrapper
│   │   ├── nlp_service.py          # HuggingFace NLP
│   │   └── gmail_service.py        # Gmail OAuth flow
│   └── web/
│       ├── auth_routes.py          # Login, signup, OAuth, settings
│       └── telegram_routes.py      # Telegram webhooks
├── templates/
│   ├── base.html                   # Base layout
│   ├── login.html                  # Login page
│   ├── signup.html                 # Signup page
│   ├── dashboard.html              # Main voicemail dashboard
│   ├── settings.html               # Service settings
│   └── error.html                  # Error page
├── static/
│   ├── css/
│   │   └── style.css               # Global styles
│   └── js/
│       ├── app.js                  # App initialization
│       ├── api.js                  # API client
│       └── audio.js                # Web Audio API
├── test/
│   ├── test_app.py
│   ├── test_voice_multilang.py
│   ├── test_auth_phase3_6.py       # Auth routes
│   ├── test_messaging_service_user_tokens.py
│   └── ...
├── docs/
│   ├── SETUP_GUIDE.md
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   └── DEPLOYMENT.md
├── .github/
│   └── workflows/
│       └── python-app.yml          # CI/CD
├── .env.example                    # Example environment variables
├── requirements.txt                # Python dependencies
├── README.md                        # Project README
└── PLAN.md                          # Development roadmap
```

---

## Database Schema

### Users
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(256) UNIQUE NOT NULL,
    name VARCHAR(256),
    hashed_password VARCHAR(512),
    created_at DATETIME DEFAULT NOW
);
```

### User Tokens (Gmail OAuth, Telegram)
```sql
CREATE TABLE user_tokens (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY REFERENCES users(id),
    service VARCHAR(128),  -- 'gmail' or 'telegram'
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    expires_at DATETIME,
    created_at DATETIME DEFAULT NOW
);
```

### Email Messages
```sql
CREATE TABLE email_messages (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY REFERENCES users(id),
    gmail_id VARCHAR(256),
    subject VARCHAR(256) NOT NULL,
    body TEXT,
    to VARCHAR(256) NOT NULL,
    created_at DATETIME DEFAULT NOW
);
```

### Telegram Conversations
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER FOREIGN KEY REFERENCES users(id),
    telegram_chat_id VARCHAR(128) UNIQUE NOT NULL,
    state VARCHAR(50),
    context TEXT,
    created_at DATETIME DEFAULT NOW,
    updated_at DATETIME DEFAULT NOW
);
```

### Messages
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER FOREIGN KEY REFERENCES conversations(id),
    sender VARCHAR(50),  -- 'user' or 'bot'
    text TEXT NOT NULL,
    created_at DATETIME DEFAULT NOW
);
```

---

## Service Layers

### Authentication (`src/services/auth.py`)
- `hash_password()` — Hash passwords with bcrypt
- `verify_password()` — Verify hashed passwords
- `register_token()` — Store user OAuth tokens

### Voice (`src/services/voice.py`)
- `transcribe_audio()` — Whisper transcription with language detection
- `speak_text()` — gTTS multi-language TTS

### Email (`src/services/email_service.py`)
- `send_email()` — Gmail API send (requires user token)
- `list_emails()` — Gmail API list inbox
- `read_email()` — Gmail API read single message

### NLP (`src/services/nlp_service.py`)
- `summarize_text()` — HuggingFace T5 summarization
- `suggest_replies()` — Generate reply suggestions

### Messaging (`src/services/messaging_service.py`)
- `send_telegram_message()` — Send Telegram message (user or env token)

### Gmail OAuth (`src/services/gmail_service.py`)
- `get_authorization_url()` — Generate OAuth flow URL
- `exchange_authorization_response_for_credentials()` — Exchange code for tokens

---

## Auth Flow

### Email/Password Login & Signup
1. User fills form at `/auth/login` or `/auth/signup`
2. Password hashed with bcrypt
3. User stored in `users` table
4. Session set with `user_id` and `user_email`
5. Redirected to `/dashboard`

### Google OAuth
1. User clicks "Login with Google" on `/auth/login?next=dashboard`
2. Redirected to `/auth/login-oauth?next=dashboard`
3. User authorizes at Google → redirected to `/auth/google/callback?code=...&state=...`
4. Backend exchanges code for credentials
5. User email fetched → User created/updated in DB
6. Gmail token stored in `user_tokens` table
7. Session set → redirected to `next` destination

### Service Connection from Settings
1. User visits `/settings`
2. Clicks "Connect Gmail" → calls `/settings/gmail/connect`
3. Same OAuth flow, but `next=settings` so user returns to settings after auth
4. User can submit Telegram bot token via `/settings/telegram` POST
5. Token stored in `user_tokens` table with `service='telegram'`

---

## Frontend Architecture

### Jinja2 Templates
- `base.html` — Navigation, header, footer
- `login.html` — Email/password + OAuth forms
- `dashboard.html` — Voicemail inbox layout with service status
- `settings.html` — Gmail/Telegram connection UI

### Vanilla JavaScript
- `api.js` — Fetch wrapper for all API calls
- `audio.js` — Web Audio API for recording and upload
- `app.js` — Page initialization and event handlers

### Styling
- `style.css` — Global styles + voicemail dashboard styles
- CSS variables for themes (blue, text colors, etc.)

---

## API Blueprint Structure

```
Flask App
├── auth_bp (src/web/auth_routes.py)
│   ├── /auth/login
│   ├── /auth/signup
│   ├── /auth/login-oauth
│   ├── /auth/google/callback
│   ├── /auth/logout
│   ├── /auth/status
│   ├── /dashboard
│   ├── /settings
│   ├── /settings/gmail/connect
│   └── /settings/telegram
├── telegram_bp (src/web/telegram_routes.py)
│   └── /webhook/telegram
└── Main routes (src/app.py)
    ├── /
    ├── /health
    ├── /voice/transcribe
    ├── /voice/speak
    ├── /email/send
    ├── /email/list
    ├── /email/read/<id>
    ├── /nlp/summarize
    ├── /nlp/suggest
    └── /message/telegram
```

---

## Session Management

- Flask `session` object stores `user_id` and `user_email` after login
- OAuth state/nonce stored in session for CSRF protection
- Session cleared on logout
- All authenticated endpoints check `session.get("user_id")`

---

## Error Handling

- 400/401/409 for auth errors (bad request, unauthorized, conflict)
- 500 for server errors (logged to console)
- Error pages rendered with `templates/error.html`

---

## Testing Strategy

- **Unit Tests:** Test individual services in isolation with mocks
- **Integration Tests:** Test auth flows with mocked Google/Telegram APIs
- **Frontend Tests:** Manual testing of UI and interactions
- **Coverage Target:** 80%+

---

## Deployment Considerations

- Database: SQLite for dev, PostgreSQL recommended for production
- Secrets: Environment variables for all credentials
- HTTPS: Required for OAuth and production
- Logging: stdout for cloud platforms (Railway, Render)
- Static files: Served directly in dev, CDN for production

---

## Performance Optimizations

- Lazy load emails on dashboard (pagination)
- Cache NLP model in memory
- Use query optimization for large message lists
- Minify CSS/JS in production

---

## Security Practices

- Passwords hashed with bcrypt (not stored in plain text)
- OAuth state parameter for CSRF protection
- Session secrets configured in production
- Credentials stored in `.secrets/` (never committed)
- HTTPS enforced in production
- Rate limiting recommended for API endpoints

---

## Future Enhancements

- WhatsApp integration via Cloud API
- Admin dashboard for stats
- Voice intent recognition (command parsing)
- Desktop app wrapper (Electron)
- Multi-user support with team workspaces
