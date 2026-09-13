from datetime import datetime, timedelta

from app import db
from app.models import SecurityLog, Alert


FAILED_LOGIN_THRESHOLD = 5
CREDENTIAL_STUFFING_THRESHOLD = 3
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


def detect_credential_stuffing(source_ip):
    """
    Detect failed login attempts against multiple
    different usernames from the same source IP
    within a short time window.
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

    usernames = {
        log.username
        for log in failed_attempts
        if log.username
    }

    if len(usernames) < CREDENTIAL_STUFFING_THRESHOLD:
        return None

    existing_alert = db.session.scalar(
        db.select(Alert).where(
            Alert.alert_type == "credential_stuffing",
            Alert.source_ip == source_ip,
            Alert.status == "new"
        )
    )

    if existing_alert:
        return existing_alert

    alert = Alert(
        alert_type="credential_stuffing",
        severity="high",
        description=(
            f"Failed login attempts against "
            f"{len(usernames)} different usernames "
            f"detected from {source_ip} within "
            f"{TIME_WINDOW_MINUTES} minutes."
        ),
        source_ip=source_ip,
        detection_rule="CREDENTIAL_STUFFING",
        status="new"
    )

    db.session.add(alert)
    db.session.commit()

    return alert