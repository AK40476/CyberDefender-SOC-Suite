from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_login import login_required

from app import db
from app.models import SecurityLog
from app.services.detection_engine import detect_brute_force


logs = Blueprint("logs", __name__, url_prefix="/api/logs")


@logs.route("", methods=["POST"])
@login_required
def create_log():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON request body is required"
        }), 400

    event_type = data.get("event_type")
    message = data.get("message")

    if not event_type or not message:
        return jsonify({
            "error": "event_type and message are required"
        }), 400

    source_ip = data.get("source_ip")

    log = SecurityLog(
        timestamp=datetime.utcnow(),
        source_ip=source_ip,
        destination_ip=data.get("destination_ip"),
        username=data.get("username"),
        event_type=event_type,
        status=data.get("status"),
        message=message,
        source=data.get("source")
    )

    db.session.add(log)
    db.session.commit()

    alert = None

    if event_type == "failed_login" and data.get("source_ip"):
        alert = detect_brute_force(data.get("source_ip"))

    response = {
        "message": "Security log created successfully",
        "log_id": log.id
    }

    if alert:
        response["alert_created"] = True
        response["alert_id"] = alert.id
        response["alert_type"] = alert.alert_type
        response["severity"] = alert.severity

    return jsonify(response), 201