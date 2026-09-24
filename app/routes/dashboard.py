from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app import db
from app.models import Alert, Incident, IOC, Evidence, InvestigationTimeline
from app.services.attack_chain_service import get_correlated_attack_chains
from app.utils.decorators import role_required


dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/")
@login_required
def index():

    alerts = db.session.scalars(
        db.select(Alert)
        .order_by(Alert.created_at.desc())
    ).all()

    incidents = db.session.scalars(
        db.select(Incident)
        .order_by(Incident.created_at.desc())
    ).all()

    recent_timeline = db.session.scalars(
        db.select(InvestigationTimeline)
        .order_by(InvestigationTimeline.created_at.desc())
        .limit(5)
    ).all()

    total_alerts = len(alerts)

    high_alerts = sum(
        1 for alert in alerts
        if alert.severity == "high"
    )

    new_alerts = sum(
        1 for alert in alerts
        if alert.status == "new"
    )

    investigating_alerts = sum(
        1 for alert in alerts
        if alert.status == "investigating"
    )

    total_incidents = len(incidents)

    active_incidents = sum(
        1 for incident in incidents
        if incident.status not in ["resolved", "false_positive"]
    )

    high_incidents = sum(
        1 for incident in incidents
        if incident.severity == "high"
    )

    total_iocs = db.session.scalar(
        db.select(db.func.count(IOC.id))
    ) or 0

    total_evidence = db.session.scalar(
        db.select(db.func.count(Evidence.id))
    ) or 0

    correlated_attack_chains = get_correlated_attack_chains()

    return render_template(
        "dashboard.html",
        user=current_user,

        total_alerts=total_alerts,
        high_alerts=high_alerts,
        new_alerts=new_alerts,
        investigating_alerts=investigating_alerts,

        total_incidents=total_incidents,
        active_incidents=active_incidents,
        high_incidents=high_incidents,

        total_iocs=total_iocs,
        total_evidence=total_evidence,

        recent_alerts=alerts[:5],
        recent_incidents=incidents[:5],
        recent_timeline=recent_timeline,

        correlated_attack_chains=correlated_attack_chains
    )


@dashboard.route("/admin")
@login_required
@role_required("admin")
def admin_panel():

    return """
    <h1>CyberDefender Admin Panel</h1>
    <p>Admin authorization successful.</p>
    """
