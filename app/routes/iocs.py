from datetime import datetime
import ipaddress
import re

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models import IOC, Incident, AuditLog


iocs = Blueprint(
    "iocs",
    __name__,
    url_prefix="/iocs"
)


def validate_ioc(ioc_type, value):
    """
    Validate IOC value according to its type.
    Returns (True, None) when valid.
    Returns (False, error_message) when invalid.
    """

    if ioc_type == "ip":
        try:
            ipaddress.ip_address(value)
            return True, None
        except ValueError:
            return False, "Invalid IP address."

    if ioc_type == "domain":
        domain_pattern = (
            r"^(?=.{1,253}$)"
            r"(?:[a-zA-Z0-9]"
            r"(?:[a-zA-Z0-9-]{0,61}"
            r"[a-zA-Z0-9])?\.)+"
            r"[a-zA-Z]{2,63}$"
        )

        if re.match(domain_pattern, value):
            return True, None

        return False, "Invalid domain name."

    if ioc_type == "url":
        url_pattern = (
            r"^https?://"
            r"[^\s]+$"
        )

        if re.match(url_pattern, value, re.IGNORECASE):
            return True, None

        return False, "Invalid URL. Use http:// or https://."

    if ioc_type == "hash":
        hash_pattern = r"^(?:[a-fA-F0-9]{32}|[a-fA-F0-9]{40}|[a-fA-F0-9]{64})$"

        if re.match(hash_pattern, value):
            return True, None

        return False, (
            "Invalid hash. Supported formats are "
            "MD5, SHA-1, and SHA-256."
        )

    if ioc_type == "email":
        email_pattern = (
            r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
            r"@[a-zA-Z0-9-]+"
            r"(?:\.[a-zA-Z0-9-]+)+$"
        )

        if re.match(email_pattern, value):
            return True, None

        return False, "Invalid email address."

    return False, "Unsupported IOC type."


@iocs.route("")
@login_required
def index():

    search = request.args.get(
        "search",
        ""
    ).strip()

    ioc_type = request.args.get(
        "type",
        ""
    ).strip().lower()

    threat_level = request.args.get(
        "threat_level",
        ""
    ).strip().lower()

    query = db.select(IOC)

    if search:
        query = query.where(
            IOC.value.ilike(f"%{search}%")
        )

    if ioc_type:
        query = query.where(
            IOC.type == ioc_type
        )

    if threat_level:
        query = query.where(
            IOC.threat_level == threat_level
        )

    iocs_list = db.session.scalars(
        query.order_by(
            IOC.created_at.desc()
        )
    ).all()

    return render_template(
        "iocs.html",
        iocs=iocs_list,
        search=search,
        selected_type=ioc_type,
        selected_threat=threat_level
    )


@iocs.route("/create", methods=["GET", "POST"])
@login_required
def create():

    incidents = db.session.scalars(
        db.select(Incident)
        .order_by(Incident.created_at.desc())
    ).all()

    if request.method == "POST":

        ioc_type = request.form.get(
            "type",
            ""
        ).strip().lower()

        value = request.form.get(
            "value",
            ""
        ).strip()

        threat_level = request.form.get(
            "threat_level",
            "unknown"
        ).strip().lower()

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

        allowed_types = [
            "ip",
            "domain",
            "url",
            "hash",
            "email"
        ]

        allowed_threat_levels = [
            "unknown",
            "low",
            "medium",
            "high",
            "critical"
        ]

        if not ioc_type or not value:
            flash(
                "IOC type and value are required.",
                "error"
            )

            return render_template(
                "ioc_create.html",
                incidents=incidents
            )

        if ioc_type not in allowed_types:
            flash(
                "Invalid IOC type.",
                "error"
            )

            return render_template(
                "ioc_create.html",
                incidents=incidents
            )

        if threat_level not in allowed_threat_levels:
            flash(
                "Invalid threat level.",
                "error"
            )

            return render_template(
                "ioc_create.html",
                incidents=incidents
            )

        is_valid, validation_error = validate_ioc(
            ioc_type,
            value
        )

        if not is_valid:
            flash(
                validation_error,
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

        existing_ioc = db.session.scalar(
            db.select(IOC).where(
                IOC.type == ioc_type,
                IOC.value == value
            )
        )

        if existing_ioc:
            flash(
                f"This IOC already exists as IOC #{existing_ioc.id}.",
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