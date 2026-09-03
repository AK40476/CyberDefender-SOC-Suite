from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Incident, User, AuditLog


incidents = Blueprint(
    "incidents",
    __name__,
    url_prefix="/incidents"
)


@incidents.route("/")
@login_required
def index():
    severity = request.args.get("severity")
    status = request.args.get("status")

    query = db.select(Incident).order_by(
        Incident.created_at.desc()
    )

    if severity:
        query = query.where(Incident.severity == severity)

    if status:
        query = query.where(Incident.status == status)

    incident_list = db.session.scalars(query).all()

    return render_template(
        "incidents.html",
        incidents=incident_list,
        selected_severity=severity,
        selected_status=status
    )


@incidents.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        severity = request.form.get("severity")

        allowed_severities = [
            "low",
            "medium",
            "high",
            "critical"
        ]

        if not title:
            flash("Incident title is required.", "error")
            return redirect(url_for("incidents.create"))

        if severity not in allowed_severities:
            flash("Invalid incident severity.", "error")
            return redirect(url_for("incidents.create"))

        incident = Incident(
            title=title,
            description=description,
            severity=severity,
            status="open"
        )

        db.session.add(incident)
        db.session.flush()

        audit_log = AuditLog(
            user_id=current_user.id,
            action="create_incident",
            resource_type="incident",
            resource_id=incident.id,
            description=f"Incident #{incident.id} was created.",
            source_ip=request.remote_addr
        )

        db.session.add(audit_log)
        db.session.commit()

        flash("Incident created successfully.", "success")

        return redirect(
            url_for("incidents.detail", incident_id=incident.id)
        )

    return render_template("incident_create.html")


@incidents.route("/<int:incident_id>")
@login_required
def detail(incident_id):
    incident = db.get_or_404(Incident, incident_id)

    assigned_user = None

    if incident.assigned_to:
        assigned_user = db.session.get(
            User,
            incident.assigned_to
        )

    users = db.session.scalars(
        db.select(User).order_by(User.username)
    ).all()

    return render_template(
        "incident_detail.html",
        incident=incident,
        assigned_user=assigned_user,
        incident_users=users
    )


@incidents.route(
    "/<int:incident_id>/status",
    methods=["POST"]
)
@login_required
def update_status(incident_id):
    incident = db.get_or_404(Incident, incident_id)

    new_status = request.form.get("status")

    allowed_statuses = [
        "open",
        "investigating",
        "contained",
        "resolved",
        "false_positive"
    ]

    if new_status not in allowed_statuses:
        flash("Invalid incident status.", "error")
        return redirect(
            url_for(
                "incidents.detail",
                incident_id=incident.id
            )
        )

    old_status = incident.status

    incident.status = new_status

    if new_status == "resolved":
        incident.resolved_at = datetime.utcnow()
    else:
        incident.resolved_at = None

    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_incident_status",
        resource_type="incident",
        resource_id=incident.id,
        description=(
            f"Incident #{incident.id} status changed "
            f"from '{old_status}' to '{new_status}'."
        ),
        source_ip=request.remote_addr
    )

    db.session.add(audit_log)
    db.session.commit()

    flash(
        "Incident status updated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "incidents.detail",
            incident_id=incident.id
        )
    )


@incidents.route(
    "/<int:incident_id>/assign",
    methods=["POST"]
)
@login_required
def assign_incident(incident_id):
    incident = db.get_or_404(Incident, incident_id)

    analyst_id = request.form.get("assigned_to")

    if not analyst_id:
        incident.assigned_to = None

        assignment_description = (
            f"Incident #{incident.id} was unassigned."
        )

    else:
        try:
            analyst = db.session.get(
                User,
                int(analyst_id)
            )
        except (TypeError, ValueError):
            analyst = None

        if not analyst:
            flash(
                "Selected user does not exist.",
                "error"
            )

            return redirect(
                url_for(
                    "incidents.detail",
                    incident_id=incident.id
                )
            )

        incident.assigned_to = analyst.id

        assignment_description = (
            f"Incident #{incident.id} was assigned "
            f"to user '{analyst.username}'."
        )

    audit_log = AuditLog(
        user_id=current_user.id,
        action="assign_incident",
        resource_type="incident",
        resource_id=incident.id,
        description=assignment_description,
        source_ip=request.remote_addr
    )

    db.session.add(audit_log)
    db.session.commit()

    flash(
        "Incident assignment updated successfully.",
        "success"
    )

    return redirect(
        url_for(
            "incidents.detail",
            incident_id=incident.id
        )
    )


@incidents.route(
    "/<int:incident_id>/resolve",
    methods=["POST"]
)
@login_required
def resolve(incident_id):
    incident = db.get_or_404(Incident, incident_id)

    resolution = request.form.get("resolution")

    if not resolution:
        flash(
            "Resolution details are required.",
            "error"
        )

        return redirect(
            url_for(
                "incidents.detail",
                incident_id=incident.id
            )
        )

    old_status = incident.status

    incident.status = "resolved"
    incident.resolution = resolution
    incident.resolved_at = datetime.utcnow()

    audit_log = AuditLog(
        user_id=current_user.id,
        action="resolve_incident",
        resource_type="incident",
        resource_id=incident.id,
        description=(
            f"Incident #{incident.id} was resolved. "
            f"Previous status: '{old_status}'."
        ),
        source_ip=request.remote_addr
    )

    db.session.add(audit_log)
    db.session.commit()

    flash(
        "Incident resolved successfully.",
        "success"
    )

    return redirect(
        url_for(
            "incidents.detail",
            incident_id=incident.id
        )
    )