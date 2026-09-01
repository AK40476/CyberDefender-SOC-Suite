from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.utils.decorators import role_required


dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/")
@login_required
def index():

    return render_template(
        "dashboard.html",
        user=current_user
    )


@dashboard.route("/admin")
@login_required
@role_required("admin")
def admin_panel():

    return """
    <h1>CyberDefender Admin Panel</h1>
    <p>Admin authorization successful.</p>
    """