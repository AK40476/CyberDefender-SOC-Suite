from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Alert, User, AuditLog


alerts = Blueprint("alerts", __name__, url_prefix="/alerts")


@alerts.route("/")
@login_required
def index():

    severity = request.args.get("severity")
    status = request.args.get("status")

    query = db.select(Alert).order_by(Alert.created_at.desc())

    if severity:
        query = query.where(Alert.severity == severity)

    if status:
        query = query.where(Alert.status == status)

    alert_list = db.session.scalars(query).all()

    return render_template(
        "alerts.html",
        alerts=alert_list,
        selected_severity=severity,
        selected_status=status
    )


@alerts.route("/<int:alert_id>")
@login_required
def detail(alert_id):

    alert = db.get_or_404(Alert, alert_id)

    assigned_user = None

    if alert.assigned_to:
        assigned_user = db.session.get(User, alert.assigned_to)

    users = db.session.scalars(
        db.select(User).order_by(User.username)
    ).all()

    return render_template(
        "alert_detail.html",
        alert=alert,
        assigned_user=assigned_user,
        alert_users=users
    )


@alerts.route("/<int:alert_id>/status", methods=["POST"])
@login_required
def update_status(alert_id):

    alert = db.get_or_404(Alert, alert_id)

    new_status = request.form.get("status")

    allowed_statuses = [
        "new",
        "investigating",
        "resolved",
        "false_positive"
    ]

    if new_status not in allowed_statuses:
        flash("Invalid alert status.", "error")

        return redirect(
            url_for("alerts.detail", alert_id=alert.id)
        )

    old_status = alert.status

    alert.status = new_status

    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_alert_status",
        resource_type="alert",
        resource_id=alert.id,
        description=(
            f"Alert #{alert.id} status changed "
            f"from '{old_status}' to '{new_status}'."
        ),
        source_ip=request.remote_addr
    )

    db.session.add(audit_log)
    db.session.commit()

    flash("Alert status updated successfully.", "success")

    return redirect(
        url_for("alerts.detail", alert_id=alert.id)
    )


@alerts.route("/<int:alert_id>/assign", methods=["POST"])
@login_required
def assign_alert(alert_id):

    alert = db.get_or_404(Alert, alert_id)

    analyst_id = request.form.get("assigned_to")

    if not analyst_id:

        alert.assigned_to = None

        assignment_description = (
            f"Alert #{alert.id} was unassigned."
        )

    else:

        analyst = db.session.get(User, int(analyst_id))

        if not analyst:

            flash("Selected user does not exist.", "error")

            return redirect(
                url_for("alerts.detail", alert_id=alert.id)
            )

        alert.assigned_to = analyst.id

        assignment_description = (
            f"Alert #{alert.id} was assigned to "
            f"user '{analyst.username}'."
        )

    audit_log = AuditLog(
        user_id=current_user.id,
        action="assign_alert",
        resource_type="alert",
        resource_id=alert.id,
        description=assignment_description,
        source_ip=request.remote_addr
    )

    db.session.add(audit_log)
    db.session.commit()

    flash("Alert assignment updated successfully.", "success")

    return redirect(
        url_for("alerts.detail", alert_id=alert.id)
    )