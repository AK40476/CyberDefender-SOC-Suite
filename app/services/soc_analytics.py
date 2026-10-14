from collections import Counter

from app import db
from app.models import Alert
from app.services.risk_scoring import get_risk_priority



def get_soc_analytics():
    """
    Calculate SOC alert analytics for dashboard visualization.
    """

    alerts = db.session.scalars(
        db.select(Alert)
        .order_by(Alert.created_at.desc())
    ).all()

    status_counts = Counter(
        alert.status for alert in alerts
    )

    rule_counts = Counter(
        alert.detection_rule for alert in alerts
    )

    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    for alert in alerts:
        severity = get_risk_priority(alert.risk_score or 0)
        severity_counts[severity] += 1


    return {
        "total_alerts": len(alerts),

        "severity": {
            "critical": severity_counts.get("critical", 0),
            "high": severity_counts.get("high", 0),
            "medium": severity_counts.get("medium", 0),
            "low": severity_counts.get("low", 0)
        },

        "status": {
            "new": status_counts.get("new", 0),
            "investigating": status_counts.get("investigating", 0),
            "resolved": status_counts.get("resolved", 0),
            "false_positive": status_counts.get("false_positive", 0)
        },

        "detection_rules": dict(
            sorted(
                rule_counts.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )
    }
