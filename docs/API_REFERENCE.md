# Voice-Based Email & Messaging Assistant — API Reference

## Base URL
```
Local: http://localhost:5000
Production: https://your-domain.com
```

---

## Authentication Routes

### Login with Email/Password
**POST** `/auth/login`

```
Request (Form Data):
- email: "user@example.com"
- password: "password123"

Response (302 Redirect to /dashboard)
Location: /dashboard

Error (401):
{
  "error": "Invalid email or password"
}
```

### Sign Up
**POST** `/auth/signup`

```
Request (Form Data):
- email: "newuser@example.com"
- name: "John Doe"
- password: "password123"
- confirm_password: "password123"

Response (302 Redirect to /dashboard)
Location: /dashboard

Error (400):
{
  "error": "All fields required"
}

Error (409) — Email already exists:
{
  "error": "Email already registered"
}
```

### Google OAuth Login
**GET** `/auth/login-oauth?next=dashboard`

Redirects to Google LOGIN page. After authorization, exchanges code for credentials and redirects to `next` destination.

### Google OAuth Callback
**GET** `/auth/google/callback?code=...&state=...`

Internal callback endpoint. Automatically called by Google after user authorizes.

### Logout
**GET** `/auth/logout`

Clears session. Redirects to `/`.

### Auth Status
**GET** `/auth/status`

```json
{
  "authenticated": true,
  "user_email": "user@example.com",
  "gmail_enabled": true,
  "gmail_connected": true,
  "telegram_connected": false
}
```

### Dashboard
**GET** `/dashboard`

Requires authentication. Returns HTML page with voicemail dashboard and service status.

---

## Settings Routes

### Get Settings Page
**GET** `/settings`

Requires authentication. Returns settings HTML page.

### Connect Gmail from Settings
**GET** `/settings/gmail/connect`

Initiates OAuth flow from settings page. After auth, user returns to `/settings`.

### Update Telegram Token
**POST** `/settings/telegram`

```
Request (Form Data):
- telegram_token: "123456789:ABCxyz..."

Response (302 Redirect to /settings)
Location: /settings?success=Token+saved

Error (400):
{
  "error": "Telegram bot token cannot be empty"
}
```

---

## Email Routes

### Send Email
**POST** `/email/send`

Requires authentication if `GMAIL_API_ENABLED=true`.

```json
{
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "This is the email body"
}

Response (200):
{
  "status": "sent",
  "message_id": "abc123..."
}

Error (400):
{
  "error": "to, subject, body are required"
}

Error (401):
{
  "error": "authentication required"
}
```

### List Emails
**GET** `/email/list`

Requires authentication if `GMAIL_API_ENABLED=true`.

```json
Response (200):
{
  "status": "ok",
  "emails": [
    {
      "id": "message_id_1",
      "from": "sender@example.com",
      "subject": "Meeting Tomorrow",
      "preview": "Hi, can we reschedule...",
      "date": "2026-04-08T10:30:00Z"
    }
  ]
}

Error (401):
{
  "error": "authentication required"
}
```

### Read Email
**GET** `/email/read/<message_id>`

Requires authentication if `GMAIL_API_ENABLED=true`.

```json
Response (200):
{
  "status": "ok",
  "id": "message_id_1",
  "from": "sender@example.com",
  "subject": "Meeting Tomorrow",
  "body": "Full email body content here...",
  "date": "2026-04-08T10:30:00Z"
}

Error (401):
{
  "error": "authentication required"
}
```

### Email Status
**GET** `/email/status`

```json
{
  "status": "ok",
  "email_api": "true",
  "authenticated": true
}
```

---

## Voice Routes

### Transcribe Audio
**POST** `/voice/transcribe`

Multipart form data with audio file.

```
Request:
- audio: <audio file (WAV/MP3)>

Response (200):
{
  "transcription": "Hello, this is a test message",
  "language": "en",
  "confidence": 0.95
}

Error (400):
{
  "error": "audio file is required"
}
```

### Text to Speech
**POST** `/voice/speak`

```json
{
  "text": "Hello, how are you?",
  "lang": "en"
}

Response (200):
Audio file (MP3) with Content-Type: audio/mpeg

Error (400):
{
  "error": "text is required"
}
```

---

## NLP Routes

### Summarize Text
**POST** `/nlp/summarize`

```json
{
  "text": "Long email or message to summarize..."
}

Response (200):
{
  "summary": "Short summary of the text",
  "language": "en"
}

Error (500):
{
  "error": "Error message"
}
```

### Suggest Replies
**POST** `/nlp/suggest`

```json
{
  "text": "Can we reschedule our meeting?"
}

Response (200):
{
  "suggestions": [
    "Sure, let's pick another time.",
    "How about next Tuesday at 2 PM?",
    "I'm free all week."
  ],
  "language": "en"
}

Error (500):
{
  "error": "Error message"
}
```

---

## Telegram Routes

### Telegram Webhook
**POST** `/webhook/telegram`

Telegram sends updates to this endpoint. Used for production deployments.

```json
Example incoming update:
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {"id": 987654321, "first_name": "John"},
    "chat": {"id": 987654321, "type": "private"},
    "text": "/help"
  }
}

Response: HTTP 200 OK
```

### Send Telegram Message
**POST** `/message/telegram`

```json
{
  "chat_id": "987654321",
  "text": "Hello from the voice assistant!"
}

Response (200):
{
  "status": "sent",
  "telegram_response": {...}
}

Error (400):
{
  "error": "chat_id and text are required"
}

Error (stub):
{
  "status": "stub",
  "message": "Telegram bot token not set."
}
```

---

## Health Check

### App Health
**GET** `/health`

```json
{
  "status": "ok"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error description",
  "status_code": 400
}
```

**Common Status Codes:**
- `200` — Success
- `302` — Redirect
- `400` — Bad Request (missing fields, invalid input)
- `401` — Unauthorized (authentication required)
- `409` — Conflict (email already exists)
- `500` — Server Error
