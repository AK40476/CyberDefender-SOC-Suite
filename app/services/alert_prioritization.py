from app.services.correlation_engine import correlate_alert


def calculate_alert_priority(alert):
    """
    Calculate operational priority for an alert.

    Priority is derived from the existing risk score,
    severity, and correlation information.
    """

    correlation = correlate_alert(alert)

    risk_score = alert.risk_score or 0
    severity = (alert.severity or "medium").lower()

    if correlation["correlated"] and (
        risk_score >= 80 or severity == "critical"
    ):
        return "critical"

    if risk_score >= 80 or severity == "critical":
        return "critical"

    if correlation["correlated"] and (
        risk_score >= 60 or severity == "high"
    ):
        return "high"

    if risk_score >= 60 or severity == "high":
        return "high"

    if risk_score >= 30 or severity == "medium":
        return "medium"

    return "low"


def get_prioritized_alerts(alerts, limit=10):
    """
    Return alerts ordered by operational priority.

    Higher priority alerts appear first. Within the same
    priority, higher risk scores and newer alerts appear first.
    """

    priority_order = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1
    }

    prioritized = []

    for alert in alerts:
        priority = calculate_alert_priority(alert)

        prioritized.append({
            "alert": alert,
            "priority": priority
        })

    prioritized.sort(
        key=lambda item: (
            priority_order[item["priority"]],
            item["alert"].risk_score or 0,
            item["alert"].created_at
        ),
        reverse=True
    )

    return prioritized[:limit]
