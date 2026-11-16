from app import create_app, db
from app.models import Alert
from app.services.alert_prioritization import calculate_alert_priority

# These are manually assigned demonstration risk scores.
# They are illustrative scenarios, not calculated by the
# application's calculate_risk_score() function.

DEMO_ALERTS = [
    {
        "alert_type": "malware_indicator",
        "severity": "critical",
        "risk_score": 85,
        "source_ip": "192.0.2.21",
        "detection_rule": "DEMO_SIMULATED_CRITICAL",
        "description": "[SIMULATED DEMO] Critical-priority scenario: suspected malware beaconing from a test endpoint. Investigate network connections and endpoint telemetry.",
    },
    {
        "alert_type": "suspicious_ip_activity",
        "severity": "high",
        "risk_score": 70,
        "source_ip": "192.0.2.22",
        "detection_rule": "DEMO_SIMULATED_HIGH",
        "description": "[SIMULATED DEMO] High-priority scenario: repeated connections to a simulated threat-intelligence indicator. Validate the destination and review related logs.",
    },
    {
        "alert_type": "privilege_escalation",
        "severity": "medium",
        "risk_score": 45,
        "source_ip": "192.0.2.23",
        "detection_rule": "DEMO_SIMULATED_MEDIUM",
        "description": "[SIMULATED DEMO] Medium-priority scenario: unusual privilege-related activity. Review account activity and authorization logs.",
    },
    {
        "alert_type": "unusual_login",
        "severity": "medium",
        "risk_score": 40,
        "source_ip": "192.0.2.24",
        "detection_rule": "DEMO_SIMULATED_MEDIUM",
        "description": "[SIMULATED DEMO] Medium-priority scenario: login activity outside the expected pattern. Check authentication history and verify with the account owner.",
    },
    {
        "alert_type": "policy_violation",
        "severity": "low",
        "risk_score": 20,
        "source_ip": "192.0.2.25",
        "detection_rule": "DEMO_SIMULATED_LOW",
        "description": "[SIMULATED DEMO] Low-priority scenario: a minor security policy deviation requiring routine review.",
    },
    {
        "alert_type": "unusual_dns_query",
        "severity": "low",
        "risk_score": 15,
        "source_ip": "192.0.2.26",
        "detection_rule": "DEMO_SIMULATED_LOW",
        "description": "[SIMULATED DEMO] Low-priority scenario: an unusual DNS query observed in test telemetry. Review the query and determine whether it is benign.",
    },
]

app = create_app()

with app.app_context():
    added = 0

    for item in DEMO_ALERTS:
        exists = db.session.scalar(
            db.select(Alert.id).where(
                Alert.detection_rule == item["detection_rule"],
                Alert.source_ip == item["source_ip"],
                Alert.description == item["description"],
            )
        )

        if exists:
            print(f"Already exists; skipped: {item['alert_type']}")
            continue

        alert = Alert(**item, status="new")
        db.session.add(alert)
        added += 1

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    alerts = db.session.scalars(
        db.select(Alert).order_by(Alert.id)
    ).all()

    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}

    print(f"\nAdded {added} simulated alerts.")
    print("\nCurrent alert list:")

    for alert in alerts:
        priority = calculate_alert_priority(alert)
        counts[priority] += 1
        print(
            f"ID={alert.id} | {priority.upper():8} | "
            f"Risk={alert.risk_score:3} | "
            f"Status={alert.status} | {alert.alert_type} | "
            f"{'[SIMULATED]' if alert.description.startswith('[SIMULATED DEMO]') else '[DETECTION ENGINE]'}"
        )

    print("\nDashboard priority totals:")
    for priority, count in counts.items():
        print(f"{priority.capitalize()}: {count}")
    print(f"TOTAL: {len(alerts)}")
