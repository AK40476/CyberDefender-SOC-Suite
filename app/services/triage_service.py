from app.services.alert_prioritization import get_prioritized_alerts


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
        if alert.status in summary:
            summary[alert.status] += 1

        severity = (alert.severity or "medium").lower()

        if severity in {
            "critical",
            "high",
            "medium",
            "low"
        }:
            summary[severity] += 1

    return summary
