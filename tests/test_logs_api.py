
from app import db
from app.models import SecurityLog


def test_create_log_successfully(authenticated_client, app):
    response = authenticated_client.post(
        "/api/logs",
        json={
            "event_type": "login",
            "message": "Successful test login",
            "source_ip": "192.0.2.10",
            "status": "success",
            "username": "test_analyst",
            "source": "pytest",
        },
    )

    assert response.status_code == 201

    data = response.get_json()
    assert data["message"] == "Security log created successfully"
    assert "log_id" in data

    with app.app_context():
        log = db.session.get(SecurityLog, data["log_id"])

        assert log is not None
        assert log.event_type == "login"
        assert log.source_ip == "192.0.2.10"
        assert log.status == "success"


def test_create_log_rejects_empty_json(authenticated_client):
    response = authenticated_client.post(
        "/api/logs",
        json={},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "JSON request body is required"
    )


def test_create_log_requires_event_type(authenticated_client):
    response = authenticated_client.post(
        "/api/logs",
        json={
            "message": "Missing event type",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "event_type and message are required"
    )


def test_create_log_requires_message(authenticated_client):
    response = authenticated_client.post(
        "/api/logs",
        json={
            "event_type": "login",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == (
        "event_type and message are required"
    )


def test_create_log_requires_authentication(client):
    response = client.post(
        "/api/logs",
        json={
            "event_type": "login",
            "message": "Unauthenticated test",
        },
    )

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
