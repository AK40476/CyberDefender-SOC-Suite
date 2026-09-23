from datetime import datetime, timedelta

from app import db
from app.models import Alert


CORRELATION_WINDOW_MINUTES = 10
MIN_RELATED_ALERTS = 2


def find_related_alerts(source_ip, reference_time=None):
    """
    Find alerts from the same source IP within
    the configured correlation time window.
    """

    if not source_ip:
        return []

    if reference_time is None:
        reference_time = datetime.utcnow()

    window_start = reference_time - timedelta(
        minutes=CORRELATION_WINDOW_MINUTES
    )

    alerts = db.session.scalars(
        db.select(Alert)
        .where(
            Alert.source_ip == source_ip,
            Alert.created_at >= window_start,
            Alert.created_at <= reference_time
        )
        .order_by(Alert.created_at.asc())
    ).all()

    return alerts


def classify_attack_chain(alerts):
    """
    Classify a correlated group of alerts based on
    the detection rules present in the group.
    """

    rules = {
        alert.detection_rule
        for alert in alerts
        if alert.detection_rule
    }

    if {
        "BRUTE_FORCE_LOGIN",
        "CREDENTIAL_STUFFING",
        "IOC_MATCH"
    }.issubset(rules):
        return "MULTI_STAGE_ATTACK"

    if {
        "BRUTE_FORCE_LOGIN",
        "IOC_MATCH"
    }.issubset(rules):
        return "BRUTE_FORCE_IOC_CHAIN"

    if {
        "BRUTE_FORCE_LOGIN",
        "CREDENTIAL_STUFFING"
    }.issubset(rules):
        return "CREDENTIAL_ATTACK_CHAIN"

    if {
        "CREDENTIAL_STUFFING",
        "IOC_MATCH"
    }.issubset(rules):
        return "CREDENTIAL_IOC_CHAIN"

    if len(rules) >= 2:
        return "CORRELATED_ACTIVITY"

    return None


def is_correlated_attack(alerts):
    """
    Determine whether a group of alerts represents
    correlated activity.
    """

    if len(alerts) < MIN_RELATED_ALERTS:
        return False

    return classify_attack_chain(alerts) is not None


def correlate_alert(alert):
    """
    Analyze a newly created alert and determine whether
    it belongs to a correlated attack chain.
    """

    if not alert or not alert.source_ip:
        return {
            "correlated": False,
            "alert_count": 0,
            "attack_chain": None,
            "alerts": []
        }

    related_alerts = find_related_alerts(
        alert.source_ip,
        alert.created_at
    )

    attack_chain = classify_attack_chain(related_alerts)

    return {
        "correlated": attack_chain is not None,
        "alert_count": len(related_alerts),
        "attack_chain": attack_chain,
        "alerts": related_alerts
    }