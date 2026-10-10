from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Alert, AuditLog
from app.services.risk_scoring import get_risk_priority

alerts = Blueprint("alerts", __name__, url_prefix="/alerts")


@alerts.route("")
@login_required
def alert_dashboard():

    alerts_list = db.session.scalars(
        db.select(Alert)
        .order_by(Alert.created_at.desc())
    ).all()

    total_alerts = len(alerts_list)

    high_alerts = sum(
        1 for alert in alerts_list
        if get_risk_priority(alert.risk_score or 0) == "high"
    )

    new_alerts = sum(
        1 for alert in alerts_list
        if alert.status == "new"
    )

    investigating_alerts = sum(
        1 for alert in alerts_list
        if alert.status == "investigating"
    )

    return render_template(
        "alerts.html",
        alerts=alerts_list,
        total_alerts=total_alerts,
        high_alerts=high_alerts,
        new_alerts=new_alerts,
        investigating_alerts=investigating_alerts
        get_risk_priority=get_risk_priority
    )


@alerts.route("/<int:alert_id>")
@login_required
def alert_detail(alert_id):

    alert = db.get_or_404(Alert, alert_id)

    from app.services.correlation_engine import correlate_alert

    correlation = correlate_alert(alert)

    return render_template(
        "alert_detail.html",
        alert=alert,
        correlation=correlation
    )


@alerts.route("/<int:alert_id>/investigate", methods=["POST"])
@login_required
def investigate_alert(alert_id):

    alert = db.get_or_404(Alert, alert_id)

    previous_status = alert.status

    if alert.status == "new":
        alert.status = "investigating"

        audit = AuditLog(
            user_id=current_user.id,
            action="start_alert_investigation",
            resource_type="alert",
            resource_id=alert.id,
            description=(
                f"Alert #{alert.id} investigation started. "
                f"Previous status: '{previous_status}'."
            )
        )

        db.session.add(audit)
        db.session.commit()

        flash(
            f"Alert #{alert.id} is now under investigation.",
            "success"
        )

    else:
        flash(
            f"Alert #{alert.id} is already '{alert.status}'.",
            "info"
        )

    return redirect(
        url_for("alerts.alert_detail", alert_id=alert.id)
    )