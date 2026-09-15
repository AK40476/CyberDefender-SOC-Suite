from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user

from app import db
from app.models import User


auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = db.session.scalar(
            db.select(User).where(User.username == username)
        )

        if user and user.is_active and user.check_password(password):
            login_user(user)

            return redirect(url_for("dashboard.index"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@auth.route("/logout")
def logout():

    logout_user()

    return redirect(url_for("auth.login"))