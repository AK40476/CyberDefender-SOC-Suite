from app.services.alert_prioritization import get_prioritized_alerts
from app.services.risk_scoring import get_risk_priority


ACTIVE_STATUSES = {"new", "investigating"}


def get_active_alerts(alerts):
    """
    Return alerts that still require analyst attention.
    """

    return [
        alert
        for alert in alerts
        if alert.status in ACTIVE_STATUSES
    ]


def get_triage_queue(alerts, limit=10):
    """
    Return active alerts ordered by operational priority.
    """

    active_alerts = get_active_alerts(alerts)

    return get_prioritized_alerts(
        active_alerts,
        limit=limit
    )


def get_triage_summary(alerts):
    """
    Return summary statistics for the active investigation queue.
    Severity is derived from risk score, not stored alert severity.
    """

    active_alerts = get_active_alerts(alerts)

    summary = {
        "total_active": len(active_alerts),
        "new": 0,
        "investigating": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for alert in active_alerts:
        if alert.status in {"new", "investigating"}:
            summary[alert.status] += 1

        severity = get_risk_priority(alert.risk_score or 0)
        summary[severity] += 1

    return summary
