from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import IOC, Incident, AuditLog


iocs = Blueprint(
    "iocs",
    __name__,
    url_prefix="/iocs"
)


@iocs.route("")
@login_required
def index():

    iocs_list = db.session.scalars(
        db.select(IOC)
        .order_by(IOC.created_at.desc())
    ).all()

    return render_template(
        "iocs.html",
        iocs=iocs_list
    )


@iocs.route("/create", methods=["GET", "POST"])
@login_required
def create():

    incidents = db.session.scalars(
        db.select(Incident)
        .order_by(Incident.created_at.desc())
    ).all()

    if request.method == "POST":

        ioc_type = request.form.get("type", "").strip()
        value = request.form.get("value", "").strip()
        threat_level = request.form.get(
            "threat_level",
            "unknown"
        ).strip()
        confidence_raw = request.form.get(
            "confidence",
            "0"
        ).strip()
        source = request.form.get(
            "source",
            ""
        ).strip()

        incident_id_raw = request.form.get(
            "incident_id",
            ""
        ).strip()

        if not ioc_type or not value:
            flash(
                "IOC type and value are required.",
                "error"
            )

            return render_template(
                "ioc_create.html",
                incidents=incidents
            )

        try:
            confidence = int(confidence_raw)
        except ValueError:
            flash(
                "Confidence must be a number between 0 and 100.",
                "error"
            )

            return render_template(
                "ioc_create.html",
                incidents=incidents
            )

        if confidence < 0 or confidence > 100:
            flash(
                "Confidence must be between 0 and 100.",
                "error"
            )

            return render_template(
                "ioc_create.html",
                incidents=incidents
            )

        incident_id = None

        if incident_id_raw:
            try:
                incident_id = int(incident_id_raw)
            except ValueError:
                flash(
                    "Invalid incident selected.",
                    "error"
                )

                return render_template(
                    "ioc_create.html",
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
                    "ioc_create.html",
                    incidents=incidents
                )

        now = datetime.utcnow()

        ioc = IOC(
            type=ioc_type,
            value=value,
            threat_level=threat_level,
            confidence=confidence,
            source=source or None,
            first_seen=now,
            last_seen=now,
            incident_id=incident_id,
            created_by=current_user.id
        )

        db.session.add(ioc)
        db.session.flush()

        audit = AuditLog(
            user_id=current_user.id,
            action="create_ioc",
            resource_type="ioc",
            resource_id=ioc.id,
            description=(
                f"IOC #{ioc.id} ({ioc.type}: {ioc.value}) "
                f"was created."
            ),
            source_ip=request.remote_addr
        )

        db.session.add(audit)
        db.session.commit()

        flash(
            f"IOC #{ioc.id} created successfully.",
            "success"
        )

        return redirect(
            url_for(
                "iocs.detail",
                ioc_id=ioc.id
            )
        )

    return render_template(
        "ioc_create.html",
        incidents=incidents
    )


@iocs.route("/<int:ioc_id>")
@login_required
def detail(ioc_id):

    ioc = db.get_or_404(
        IOC,
        ioc_id
    )

    return render_template(
        "ioc_detail.html",
        ioc=ioc
    )