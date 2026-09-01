from app import create_app, db
from app.models import User


app = create_app()


with app.app_context():

    existing_user = db.session.scalar(
        db.select(User).where(User.username == "analyst")
    )

    if existing_user:
        print("Analyst user already exists.")

    else:
        analyst = User(
            username="analyst",
            email="analyst@cyberdefender.local",
            role="analyst",
            is_active=True
        )

        analyst.set_password("Analyst123!")

        db.session.add(analyst)
        db.session.commit()

        print("Analyst user created successfully.")