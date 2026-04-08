# Voice-Based Email & Messaging Assistant — Setup Guide

## Overview
This guide walks you through setting up the Voice-Based Email & Messaging Assistant for local development and deployment.

---

## Local Development Setup

### Prerequisites
- Python 3.8+
- Git
- Virtual environment tool (`venv` or `conda`)

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-org/Voice-Based-Email-Messaging-Assistant.git
cd Voice-Based-Email-Messaging-Assistant
```

### Step 2: Create and Activate Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create Environment File
```bash
cp .env.example .env
```

Edit `.env` with your configuration.

### Step 5: Initialize Database
```bash
python -c "from src.db import init_db; init_db()"
```

### Step 6: Start Development Server
```bash
python -m flask run --host 0.0.0.0 --port 5000
```

App available at `http://localhost:5000`.

---

## Google OAuth Setup

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" → Name: "Voice Assistant"
3. Wait for creation

### 2. Enable Gmail API
1. Search "Gmail API" → Select → Click "Enable"

### 3. Create OAuth Credentials
1. Go to "Credentials" → "Create Credentials" → "OAuth client ID"
2. Select "Web application"
3. Add Authorized Redirect URIs:
   - Dev: `http://localhost:5000/auth/google/callback`
   - Prod: `https://your-domain.com/auth/google/callback`
4. Click "Create"

### 4. Download Credentials
1. Download JSON file → Save to `.secrets/client_secret_XXXX.json`
2. Add `.secrets/` to `.gitignore`

### 5. Configure `.env`
```env
GMAIL_API_ENABLED=true
GOOGLE_OAUTH_CREDENTIALS_PATH=.secrets/client_secret_XXXX.json
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/auth/google/callback
```

---

## Telegram Bot Setup

### 1. Create Bot
1. Open Telegram → Search `@BotFather`
2. Send `/newbot` → Follow prompts
3. Copy bot token: `123456789:ABCxyz...`

### 2. Configure `.env`
```env
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
```

### 3. Production Webhook (Optional)
```bash
curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://your-domain.com/webhook/telegram\"}"
```

---

## Environment Variables

```env
# Flask
FLASK_APP=src.app
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-prod

# Database
DATABASE_URL=sqlite:///./data.db

# Gmail
GMAIL_API_ENABLED=true
GOOGLE_OAUTH_CREDENTIALS_PATH=.secrets/client_secret_XXXX.json
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/auth/google/callback

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token

# AI Models
NLP_MODEL=google/flan-t5-small
TORCH_DEVICE=cpu

# Logging
LOG_LEVEL=INFO

# Optional: Sentry
SENTRY_DSN=
```

---

## Running Tests

```bash
# All tests
python -m pytest test/ -v

# With coverage
python -m pytest test/ --cov=src --cov-report=html

# Specific test
python -m pytest test/test_auth_phase3_6.py -v
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| ModuleNotFoundError: src | Activate venv, run from project root |
| Credentials not found | Check `.secrets/` path in `.env` |
| Port already in use | Use `python -m flask run --port 5001` |
| Telegram not responding | Verify TELEGRAM_BOT_TOKEN is correct |

---

## Next Steps
- [ARCHITECTURE.md](ARCHITECTURE.md) — Project structure
- [API_REFERENCE.md](API_REFERENCE.md) — All endpoints
- [DEPLOYMENT.md](DEPLOYMENT.md) — Production deployment
