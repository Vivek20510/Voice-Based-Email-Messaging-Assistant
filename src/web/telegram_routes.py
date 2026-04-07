from flask import Blueprint, request, jsonify
from src.services.telegram_service import handle_update

telegram_bp = Blueprint("telegram", __name__)


@telegram_bp.route("/telegram/webhook", methods=["POST"])
def telegram_webhook():
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify({"status": "error", "error": "Invalid request payload"}), 400

    result = handle_update(payload)
    if result.get("status") == "error":
        return jsonify(result), 500
    return jsonify(result)


@telegram_bp.route("/telegram/ping", methods=["GET"])
def telegram_ping():
    return jsonify({"status": "ok", "message": "Telegram webhook is active."})
