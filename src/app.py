import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
from pathlib import Path
from flask import Flask, jsonify, request, session, render_template, redirect, url_for
from src.services.voice import transcribe_audio, speak_text
from src.services.email_service import send_email, list_emails, read_email
from src.services.messaging_service import send_telegram_message
from src.services.nlp_service import summarize_text, suggest_replies
from src.db import init_db
from src.web.auth_routes import auth_bp
from src.web.telegram_routes import telegram_bp

BASE_DIR = Path(__file__).resolve().parent.parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")
app.register_blueprint(auth_bp)
app.register_blueprint(telegram_bp)


def setup():
    init_db()


with app.app_context():
    setup()


@app.route("/favicon.ico")
def favicon():
    return "", 204


@app.route("/")
def home():
    # Redirect authenticated users to dashboard
    if session.get("user_email"):
        return redirect(url_for("auth.dashboard"))
    return render_template("login.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/voice/transcribe", methods=["POST"])
def voice_transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "audio file is required"}), 400

    file = request.files["audio"]
    transcription = transcribe_audio(file)
    return jsonify(transcription)


@app.route("/voice/speak", methods=["POST"])
def voice_speak():
    from flask import send_file

    payload = request.get_json(force=True)
    text = payload.get("text")
    lang = payload.get("lang", "en")
    if not text:
        return jsonify({"error": "text is required"}), 400
    audio_path = speak_text(text, lang)
    return send_file(audio_path, as_attachment=True, download_name="speech.mp3")


@app.route("/email/send", methods=["POST"])
def api_send_email():
    gmail_enabled = os.getenv("GMAIL_API_ENABLED", "false").lower() in [
        "1",
        "true",
        "yes",
    ]
    if gmail_enabled and not session.get("user_id"):
        return jsonify({"error": "authentication required"}), 401

    payload = request.get_json(force=True)
    to = payload.get("to")
    subject = payload.get("subject")
    body = payload.get("body")
    if not all([to, subject, body]):
        return jsonify({"error": "to, subject, body are required"}), 400

    result = send_email(to, subject, body, user_id=session.get("user_id"))
    return jsonify(result)


@app.route("/email/status", methods=["GET"])
def api_email_status():
    return jsonify(
        {
            "status": "ok",
            "email_api": os.getenv("GMAIL_API_ENABLED", "false"),
            "authenticated": bool(session.get("user_id")),
        }
    )


@app.route("/email/list", methods=["GET"])
def api_email_list():
    gmail_enabled = os.getenv("GMAIL_API_ENABLED", "false").lower() in [
        "1",
        "true",
        "yes",
    ]
    if gmail_enabled and not session.get("user_id"):
        return jsonify({"error": "authentication required"}), 401

    result = list_emails(session.get("user_id"))
    return jsonify(result)


@app.route("/email/read/<message_id>", methods=["GET"])
def api_email_read(message_id):
    gmail_enabled = os.getenv("GMAIL_API_ENABLED", "false").lower() in [
        "1",
        "true",
        "yes",
    ]
    if gmail_enabled and not session.get("user_id"):
        return jsonify({"error": "authentication required"}), 401

    result = read_email(session.get("user_id"), message_id)
    return jsonify(result)


@app.route("/nlp/summarize", methods=["POST"])
def api_nlp_summarize():
    payload = request.get_json(force=True)
    text = payload.get("text")
    if not text:
        return jsonify({"error": "text is required"}), 400

    try:
        result = summarize_text(text)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/nlp/suggest", methods=["POST"])
def api_nlp_suggest():
    payload = request.get_json(force=True)
    text = payload.get("text")
    if not text:
        return jsonify({"error": "text is required"}), 400

    try:
        result = suggest_replies(text)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/message/telegram", methods=["POST"])
def api_send_telegram():
    payload = request.get_json(force=True)
    chat_id = payload.get("chat_id")
    text = payload.get("text")
    if not all([chat_id, text]):
        return jsonify({"error": "chat_id and text are required"}), 400

    result = send_telegram_message(chat_id, text)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
