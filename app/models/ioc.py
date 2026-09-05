from datetime import datetime

from app import db


class IOC(db.Model):
    __tablename__ = "iocs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    type = db.Column(
        db.String(20),
        nullable=False
    )

    value = db.Column(
        db.String(500),
        nullable=False
    )

    threat_level = db.Column(
        db.String(20),
        nullable=False,
        default="unknown"
    )

    confidence = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    source = db.Column(
        db.String(100),
        nullable=True
    )

    first_seen = db.Column(
        db.DateTime,
        nullable=True
    )

    last_seen = db.Column(
        db.DateTime,
        nullable=True
    )

    incident_id = db.Column(
        db.Integer,
        db.ForeignKey("incidents.id"),
        nullable=True
    )

    incident = db.relationship(
        "Incident",
        backref=db.backref(
            "iocs",
            lazy=True
        )
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<IOC {self.id} {self.type}: {self.value}>"