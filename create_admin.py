from app import create_app, db
from app.models import User


app = create_app()


with app.app_context():

    existing_user = db.session.scalar(
        db.select(User).where(User.username == "admin")
    )

    if existing_user:
        print("Admin user already exists.")

    else:
        admin = User(
            username="admin",
            email="admin@cyberdefender.local",
            role="admin",
            is_active=True
        )

        admin.set_password("ChangeMe123!")

        db.session.add(admin)
        db.session.commit()

        print("Admin user created successfully.")