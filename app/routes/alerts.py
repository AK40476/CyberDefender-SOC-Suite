from flask import Blueprint, render_template
from flask_login import login_required

from app import db
from app.models import Alert


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
        if alert.severity == "high"
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
    )