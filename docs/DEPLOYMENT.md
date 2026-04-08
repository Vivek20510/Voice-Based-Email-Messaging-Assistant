# Voice-Based Email & Messaging Assistant — Deployment Guide

## Overview
Deployment options for free/low-cost cloud platforms: Railway, Render, or self-hosted.

---

## Deployment Options

| Platform | Pricing | Pros | Cons |
|----------|---------|------|------|
| **Railway** | $5/month | Simple UI, git integration | Limited free tier |
| **Render** | Free | Long-running services, custom domains | Slower on free tier |
| **Heroku** | Paid | Mature, many add-ons | Expensive ($7+/month) |
| **Self-Hosted** | VPS cost | Full control | Requires DevOps knowledge |

---

## Railway Deployment

### Step 1: Connect GitHub Repository
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Railroad auto-detects Python + Flask

### Step 2: Set Environment Variables
In Railway dashboard:
1. Go to "Variables" tab
2. Add all environment variables:

```
FLASK_APP=src.app
FLASK_ENV=production
SECRET_KEY=your-long-random-secret
DATABASE_URL=sqlite:///./data.db
GMAIL_API_ENABLED=true
GOOGLE_OAUTH_CREDENTIALS_PATH=.secrets/client_secret_XXXX.json
GOOGLE_OAUTH_REDIRECT_URI=https://your-app.railway.app/auth/google/callback
TELEGRAM_BOT_TOKEN=your_bot_token
NLP_MODEL=google/flan-t5-small
TORCH_DEVICE=cpu
LOG_LEVEL=INFO
```

### Step 3: Upload Secrets
1. Go to Railway project → "Settings" → "Secrets"
2. Upload `.secrets/client_secret_XXXX.json` as config

Alternatively, set `GOOGLE_OAUTH_CREDENTIALS` as environment variable with JSON contents.

### Step 4: Configure OAuth Redirect URI
1. In your Google Cloud Console
2. Add redirect URI: `https://your-app.railway.app/auth/google/callback`

### Step 5: Deploy
Railway auto-deploys on GitHub push. Check deployment logs.

### Step 6: Update Telegram Webhook (Optional)
```bash
curl -X POST https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://your-app.railway.app/webhook/telegram\"}"
```

---

## Render Deployment

### Step 1: Create Web Service
1. Go to [render.com](https://render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Name: "voice-assistant"
5. Environment: "Python 3"
6. Build Command: `pip install -r requirements.txt`
7. Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT src.app:app`

### Step 2: Set Environment Variables
In Render dashboard → "Environment":

```
FLASK_APP=src.app
FLASK_ENV=production
SECRET_KEY=your-long-random-secret
DATABASE_URL=sqlite:///./data.db
GMAIL_API_ENABLED=true
TELEGRAM_BOT_TOKEN=your_bot_token
NLP_MODEL=google/flan-t5-small
TORCH_DEVICE=cpu
LOG_LEVEL=INFO
```

### Step 3: Add Secrets
1. Create `.env.production` locally with sensitive values
2. Copy contents of `.secrets/client_secret_XXXX.json`
3. Paste into `GOOGLE_OAUTH_CREDENTIALS` environment variable in Render

### Step 4: Update OAuth Redirect
In Google Cloud Console:
```
https://your-app.onrender.com/auth/google/callback
```

### Step 5: Deploy
Click "Create Web Service". Render deploys from GitHub.

---

## Production Configuration

### DATABASE_URL for PostgreSQL (Recommended)
Replace SQLite with PostgreSQL for production scalability.

```env
DATABASE_URL=postgresql://user:password@db-host:5432/voiceassistant
```

**Setup Render PostgreSQL:**
1. In Render → "Database" → "New PostgreSQL"
2. Copy connection string → Set as `DATABASE_URL`

### Gunicorn WSGI Server
Replace development Flask server with production WSGI server.

**Update start command:**
```bash
gunicorn -w 4 -b 0.0.0.0:$PORT src.app:app
```

**Ensure `requirements.txt` includes:**
```
gunicorn
```

### HTTPS / SSL
- Railway: Auto SSL (free)
- Render: Auto SSL (free)

### Domain Setup
- Railway: Get free `.railway.app` subdomain
- Render: Get free `.onrender.com` subdomain
- Custom domains: Available in both (requires DNS config)

---

## Database Migrations

### SQLite to PostgreSQL
For production, migrate from SQLite to PostgreSQL:

```bash
# Development (SQLite)
DATABASE_URL=sqlite:///./data.db python -m alembic init migrations

# Production (PostgreSQL)
DATABASE_URL=postgresql://... python -m alembic upgrade head
```

---

## Environment-Specific Secrets

### Development (.env)
```env
FLASK_ENV=development
SECRET_KEY=dev-secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:5000/auth/google/callback
```

### Production (.env.production)
```env
FLASK_ENV=production
SECRET_KEY=long-random-secret-min-32-chars
GOOGLE_OAUTH_REDIRECT_URI=https://your-app.onrender.com/auth/google/callback
```

---

## Logging & Monitoring

### Cloud Logging
- Railway/Render both capture stdout/stderr automatically
- View logs in dashboard console

### Optional: Sentry Error Tracking
1. Sign up at [sentry.io](https://sentry.io) (free tier available)
2. Create project for Python/Flask
3. Copy DSN → Set `SENTRY_DSN` environment variable
4. Install Sentry: `pip install sentry-sdk`

**In `src/app.py`:**
```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    traces_sample_rate=0.1
)
```

---

## Continuous Deployment

### GitHub Actions CI/CD
Currently: `python-app.yml` runs tests on push.

**For auto-deploy to Railway/Render:**
- Railway: Connects GitHub directly (no additional config)
- Render: Connects GitHub directly (no additional config)

Just push to `main` branch and services auto-deploy!

---

## Scaling Considerations

### Free Tier Limits
- Railway: 5GB storage, CPU-based pricing above free tier
- Render: 750 free tier hours/month (one app always running)
- Database: SQLite per app, PostgreSQL shared across replicas

### Upgrading for Production Traffic
1. **Database:** Migrate to PostgreSQL
2. **Server:** Add more Gunicorn workers
3. **Cache:** Add Redis for session/token caching
4. **CDN:** Serve static files from Cloudflare
5. **Load Balancer:** Use Railway/Render's built-in load balancing

---

## Health Checks & Monitoring

### Recommended Setup
1. Enable health check endpoint: `GET /health`
2. Railway/Render ping `/health` every 30s
3. Alert on failures

---

## Troubleshooting Deployment

### "Python version not supported"
- Ensure `runtime.txt` specifies `python-3.10` or higher

### "Secret not accessible"
- Check variable names match exactly
- Ensure no leading/trailing spaces

### "Gmail OAuth localhost redirect"
- Change `GOOGLE_OAUTH_REDIRECT_URI` when moving to production
- Update in Google Cloud Console credentials

### "Telegram webhook fails"
- Verify webhook URL is HTTPS
- Check webhook update command succeeded: `setWebhook`

### "Database locked"
- SQLite doesn't scale for concurrent writes
- Migrate to PostgreSQL for production

---

## Backup & Recovery

### SQLite Backups
For production, commit daily SQLite snapshot to Git:
```bash
git add data.db
git commit -m "Daily backup"
git push
```

Or use external backup service (AWS S3, Google Cloud Storage).

### PostgreSQL Backups
- Railway/Render provide automated backups
- Download from dashboard under "Settings" → "Backups"

---

## Rollback & Versioning

### GitHub Tags for Releases
```bash
git tag v1.0.0
git push origin v1.0.0
```

Both Railway and Render can deploy specific Git refs.

---

## Security Best Practices

1. **Secrets Management**
   - Never commit `.env` or `.secrets/`
   - Use platform's environment variable UI
   - Rotate `SECRET_KEY` monthly

2. **HTTPS**
   - Always use HTTPS in production (auto with Railway/Render)

3. **Rate Limiting**
   - Add Flask-Limiter for API protection
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: session.get('user_id'))
   ```

4. **SQL Injection**
   - Always use SQLAlchemy ORM (no raw SQL)

5. **OAuth**
   - Validate state parameter
   - Use PKCE for enhanced security
