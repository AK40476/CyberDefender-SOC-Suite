from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import Evidence, Incident, User, AuditLog


evidence = Blueprint(
    "evidence",
    __name__,
    url_prefix="/evidence"
)


@evidence.route("")
@login_required
def index():

    incident_id = request.args.get("incident_id", type=int)

    query = db.select(Evidence).order_by(
        Evidence.collected_at.desc()
    )

    if incident_id:
        query = query.where(
            Evidence.incident_id == incident_id
        )

    evidence_list = db.session.scalars(query).all()

    return render_template(
        "evidence.html",
        evidence_list=evidence_list,
        selected_incident=incident_id
    )


@evidence.route("/create", methods=["GET", "POST"])
@login_required
def create():

    incidents = db.session.scalars(
        db.select(Incident).order_by(
            Incident.created_at.desc()
        )
    ).all()

    if request.method == "POST":

        incident_id_raw = request.form.get(
            "incident_id",
            ""
        ).strip()

        evidence_type = request.form.get(
            "evidence_type",
            ""
        ).strip().lower()

        title = request.form.get(
            "title",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        file_path = request.form.get(
            "file_path",
            ""
        ).strip()

        hash_value = request.form.get(
            "hash_value",
            ""
        ).strip()

        allowed_types = [
            "log",
            "screenshot",
            "network_capture",
            "malware_sample",
            "document",
            "other"
        ]

        if not incident_id_raw:
            flash(
                "Incident selection is required.",
                "error"
            )
            return render_template(
                "evidence_create.html",
                incidents=incidents
            )

        try:
            incident_id = int(incident_id_raw)
        except ValueError:
            flash(
                "Invalid incident selected.",
                "error"
            )
            return render_template(
                "evidence_create.html",
                incidents=incidents
            )

        incident = db.session.get(
            Incident,
            incident_id
        )

        if not incident:
            flash(
                "Selected incident does not exist.",
                "error"
            )
            return render_template(
                "evidence_create.html",
                incidents=incidents
            )

        if evidence_type not in allowed_types:
            flash(
                "Invalid evidence type.",
                "error"
            )
            return render_template(
                "evidence_create.html",
                incidents=incidents
            )

        if not title:
            flash(
                "Evidence title is required.",
                "error"
            )
            return render_template(
                "evidence_create.html",
                incidents=incidents
            )

        evidence_item = Evidence(
            incident_id=incident_id,
            evidence_type=evidence_type,
            title=title,
            description=description or None,
            file_path=file_path or None,
            hash_value=hash_value or None,
            collected_by=current_user.id,
            collected_at=datetime.utcnow()
        )

        db.session.add(evidence_item)
        db.session.flush()

        audit_log = AuditLog(
            user_id=current_user.id,
            action="create_evidence",
            resource_type="evidence",
            resource_id=evidence_item.id,
            description=(
                f"Evidence #{evidence_item.id} "
                f"was added to Incident #{incident.id}."
            ),
            source_ip=request.remote_addr
        )

        db.session.add(audit_log)
        db.session.commit()

        flash(
            f"Evidence #{evidence_item.id} created successfully.",
            "success"
        )

        return redirect(
            url_for(
                "evidence.detail",
                evidence_id=evidence_item.id
            )
        )

    return render_template(
        "evidence_create.html",
        incidents=incidents
    )


@evidence.route("/<int:evidence_id>")
@login_required
def detail(evidence_id):

    evidence_item = db.get_or_404(
        Evidence,
        evidence_id
    )

    collected_by_user = None

    if evidence_item.collected_by:
        collected_by_user = db.session.get(
            User,
            evidence_item.collected_by
        )

    return render_template(
        "evidence_detail.html",
        evidence=evidence_item,
        collected_by_user=collected_by_user
    )