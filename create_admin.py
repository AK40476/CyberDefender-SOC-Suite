
from getpass import getpass

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
        password = getpass("Enter a new admin password: ")
        confirm_password = getpass("Confirm admin password: ")

        if not password:
            raise ValueError("Password cannot be empty.")

        if password != confirm_password:
            raise ValueError("Passwords do not match.")

        admin = User(
            username="admin",
            email="admin@cyberdefender.local",
            role="admin",
            is_active=True
        )

        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()

        print("Admin user created successfully.")
