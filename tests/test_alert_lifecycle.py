from app import db
from app.models import Alert, AuditLog


def create_test_alert(app):
    with app.app_context():
        alert = Alert(
            alert_type="brute_force",
            severity="high",
            risk_score=60,
            description="Five failed login attempts detected.",
            source_ip="198.51.100.50",
            detection_rule="BRUTE_FORCE_LOGIN",
            status="new",
        )
        db.session.add(alert)
        db.session.commit()
        return alert.id


def test_alert_dashboard_requires_login(client):
    response = client.get("/alerts")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_alert_dashboard_displays_alert(
    authenticated_client,
    app,
):
    create_test_alert(app)

    response = authenticated_client.get("/alerts")

    assert response.status_code == 200
    assert b"brute_force" in response.data
    assert b"198.51.100.50" in response.data
    assert b"BRUTE_FORCE_LOGIN" in response.data
    assert b"new" in response.data


def test_alert_detail_displays_alert(
    authenticated_client,
    app,
):
    alert_id = create_test_alert(app)

    response = authenticated_client.get(f"/alerts/{alert_id}")

    assert response.status_code == 200
    assert b"Five failed login attempts detected." in response.data


def test_investigate_alert_updates_status_and_creates_audit_log(
    authenticated_client,
    app,
):
    alert_id = create_test_alert(app)

    response = authenticated_client.post(
        f"/alerts/{alert_id}/investigate",
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        alert = db.session.get(Alert, alert_id)

        assert alert is not None
        assert alert.status == "investigating"

        audit = db.session.scalar(
            db.select(AuditLog).where(
                AuditLog.action == "start_alert_investigation",
                AuditLog.resource_type == "alert",
                AuditLog.resource_id == alert_id,
            )
        )

        assert audit is not None
        assert audit.description is not None


def test_reinvestigating_alert_does_not_create_duplicate_audit_log(
    authenticated_client,
    app,
):
    alert_id = create_test_alert(app)

    first_response = authenticated_client.post(
        f"/alerts/{alert_id}/investigate",
    )
    assert first_response.status_code == 302

    second_response = authenticated_client.post(
        f"/alerts/{alert_id}/investigate",
    )
    assert second_response.status_code == 302

    with app.app_context():
        audit_logs = db.session.scalars(
            db.select(AuditLog).where(
                AuditLog.action == "start_alert_investigation",
                AuditLog.resource_type == "alert",
                AuditLog.resource_id == alert_id,
            )
        ).all()

        assert len(audit_logs) == 1


def test_analyst_cannot_access_admin_panel(authenticated_client):
    response = authenticated_client.get("/admin")

    assert response.status_code == 403


def test_alert_detail_returns_404_for_missing_alert(
    authenticated_client,
):
    response = authenticated_client.get("/alerts/999999")

    assert response.status_code == 404
