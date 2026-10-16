
import pytest

from app import create_app, db


@pytest.fixture
def app(tmp_path):
    database_file = tmp_path / "test_cyberdefender.db"

    app = create_app()

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        SQLALCHEMY_DATABASE_URI=(
            f"sqlite:///{database_file.as_posix()}"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    with app.app_context():
        db.create_all()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def authenticated_client(app, client):
    from app.models import User

    with app.app_context():
        user = User(
            username="test_analyst",
            email="test_analyst@example.com",
            role="analyst",
        )
        user.set_password("TestPassword123!")

        db.session.add(user)
        db.session.commit()

    response = client.post(
        "/login",
        data={
            "username": "test_analyst",
            "password": "TestPassword123!",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    return client
