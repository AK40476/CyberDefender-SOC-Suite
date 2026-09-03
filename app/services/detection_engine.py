from datetime import datetime, timedelta

from app import db
from app.models import SecurityLog, Alert


FAILED_LOGIN_THRESHOLD = 5
TIME_WINDOW_MINUTES = 5


def detect_brute_force(source_ip):
    """
    Detect multiple failed login attempts
    from the same IP within a short time window.
    """

    window_start = datetime.utcnow() - timedelta(
        minutes=TIME_WINDOW_MINUTES
    )

    failed_attempts = db.session.scalars(
        db.select(SecurityLog).where(
            SecurityLog.source_ip == source_ip,
            SecurityLog.event_type == "failed_login",
            SecurityLog.status == "failed",
            SecurityLog.timestamp >= window_start
        )
    ).all()

    if len(failed_attempts) < FAILED_LOGIN_THRESHOLD:
        return None

    existing_alert = db.session.scalar(
        db.select(Alert).where(
            Alert.alert_type == "brute_force",
            Alert.source_ip == source_ip,
            Alert.status == "new"
        )
    )

    if existing_alert:
        return existing_alert

    alert = Alert(
        alert_type="brute_force",
        severity="high",
        description=(
            f"{len(failed_attempts)} failed login attempts "
            f"detected from {source_ip} within "
            f"{TIME_WINDOW_MINUTES} minutes."
        ),
        source_ip=source_ip,
        detection_rule="BRUTE_FORCE_LOGIN",
        status="new"
    )

    db.session.add(alert)
    db.session.commit()

    return alert