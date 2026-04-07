# Phase 2: Core Voice + Email + NLP APIs (API-only)

## Objectives
- Complete backend API for voice transcription and synthesis
- Add email integrations stubbed for early development
- Add NLP endpoints for summarization and reply generation

## Endpoints
- `GET /health`
- `POST /voice/transcribe` (multipart payload `audio`)
- `POST /voice/speak` (JSON `text`)
- `POST /email/send` (JSON `to`, `subject`, `body`)
- `GET /email/status`
- `GET /email/list` (stub)
- `GET /email/read/<message_id>` (stub)
- `POST /nlp/summarize` (JSON `text`)
- `POST /nlp/suggest` (JSON `text`)
- `POST /message/telegram` (JSON `chat_id`, `text`)
- `POST /message/telegram/webhook` (stub for incoming messages)

## Environment variables
- `DATABASE_URL` (default `sqlite:///./data.db`)
- `GMAIL_API_ENABLED` (`true` to enable real email integration)
- `TELEGRAM_BOT_TOKEN` for Telegram messaging
- `NLP_MODEL` default `google/flan-t5-small`

## Testing
- `pytest -q`
- An endpoint test coverage exists for all core routes

## Next Phase
- Add Gmail OAuth flow with `google-auth-oauthlib`
- Add Telegram webhook processing and outbound state
- Add multi-language voice command recognition
- Add UI integration (Postman/Swagger or web UI)
