from app import db
from app.models import Alert, IOC, SecurityLog


def submit_failed_login(client, source_ip, username="test_user"):
    return client.post(
        "/api/logs",
        json={
            "event_type": "failed_login",
            "message": "Invalid login attempt",
            "source_ip": source_ip,
            "username": username,
            "status": "failed",
            "source": "pytest",
        },
    )


def test_five_failed_logins_create_brute_force_alert(
    authenticated_client,
    app,
):
    source_ip = "198.51.100.10"

    for attempt in range(5):
        response = submit_failed_login(
            authenticated_client,
            source_ip,
            username=f"user_{attempt}",
        )
        assert response.status_code == 201

    with app.app_context():
        logs = db.session.scalars(
            db.select(SecurityLog).where(
                SecurityLog.source_ip == source_ip,
                SecurityLog.event_type == "failed_login",
            )
        ).all()

        alerts = db.session.scalars(
            db.select(Alert).where(
                Alert.alert_type == "brute_force",
                Alert.source_ip == source_ip,
            )
        ).all()

        assert len(logs) == 5
        assert len(alerts) == 1
        assert alerts[0].severity == "high"
        assert alerts[0].detection_rule == "BRUTE_FORCE_LOGIN"
        assert alerts[0].risk_score == 60


def test_repeated_failed_logins_do_not_duplicate_active_alert(
    authenticated_client,
    app,
):
    source_ip = "198.51.100.11"

    for attempt in range(6):
        response = submit_failed_login(
            authenticated_client,
            source_ip,
            username=f"user_{attempt}",
        )
        assert response.status_code == 201

    with app.app_context():
        alerts = db.session.scalars(
            db.select(Alert).where(
                Alert.alert_type == "brute_force",
                Alert.source_ip == source_ip,
                Alert.status == "new",
            )
        ).all()

        assert len(alerts) == 1


def test_high_threat_ip_creates_suspicious_ip_alert(
    authenticated_client,
    app,
):
    source_ip = "203.0.113.25"

    with app.app_context():
        ioc = IOC(
            type="ip",
            value=source_ip,
            threat_level="high",
            confidence=95,
            source="pytest",
        )
        db.session.add(ioc)
        db.session.commit()

    response = authenticated_client.post(
        "/api/logs",
        json={
            "event_type": "network_connection",
            "message": "Connection to a known suspicious IP",
            "source_ip": source_ip,
            "status": "observed",
            "source": "pytest",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["alert_created"] is True
    assert data["alert_type"] == "suspicious_ip_activity"
    assert data["risk_score"] == 70

    with app.app_context():
        alert = db.session.scalar(
            db.select(Alert).where(
                Alert.alert_type == "suspicious_ip_activity",
                Alert.source_ip == source_ip,
            )
        )

        assert alert is not None
        assert alert.severity == "high"
        assert alert.detection_rule == "IOC_MATCH"


def test_low_threat_ioc_does_not_create_suspicious_ip_alert(
    authenticated_client,
    app,
):
    source_ip = "203.0.113.26"

    with app.app_context():
        ioc = IOC(
            type="ip",
            value=source_ip,
            threat_level="low",
            confidence=20,
            source="pytest",
        )
        db.session.add(ioc)
        db.session.commit()

    response = authenticated_client.post(
        "/api/logs",
        json={
            "event_type": "network_connection",
            "message": "Connection to a low-threat IOC",
            "source_ip": source_ip,
            "status": "observed",
            "source": "pytest",
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert "alert_created" not in data

    with app.app_context():
        alert = db.session.scalar(
            db.select(Alert).where(
                Alert.alert_type == "suspicious_ip_activity",
                Alert.source_ip == source_ip,
            )
        )

        assert alert is None