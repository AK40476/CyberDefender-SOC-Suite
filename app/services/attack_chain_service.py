from collections import OrderedDict

from app import db
from app.models import Alert
from app.services.correlation_engine import correlate_alert


def get_correlated_attack_chains(limit=10):
    """
    Build a dashboard-friendly view of correlated attack chains.

    Each attack chain is grouped by:
        - attack chain name
        - source IP

    Returns a list of dictionaries containing the chain,
    source IP, related alerts, alert count, and highest risk.
    """

    alerts = db.session.scalars(
        db.select(Alert)
        .where(Alert.source_ip.is_not(None))
        .order_by(Alert.created_at.desc())
    ).all()

    chains = OrderedDict()

    for alert in alerts:

        correlation = correlate_alert(alert)

        if not correlation["correlated"]:
            continue

        attack_chain = correlation["attack_chain"]
        source_ip = alert.source_ip

        key = (attack_chain, source_ip)

        if key not in chains:
            chains[key] = {
                "attack_chain": attack_chain,
                "source_ip": source_ip,
                "alerts": correlation["alerts"],
                "alert_count": correlation["alert_count"],
                "highest_risk": max(
                    related_alert.risk_score
                    for related_alert in correlation["alerts"]
                )
            }

    return list(chains.values())[:limit]
