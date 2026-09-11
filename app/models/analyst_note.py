from datetime import datetime

from app import db


class AnalystNote(db.Model):
    __tablename__ = "analyst_notes"

    id = db.Column(db.Integer, primary_key=True)

    incident_id = db.Column(
        db.Integer,
        db.ForeignKey("incidents.id"),
        nullable=False
    )

    analyst_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    analyst = db.relationship(
        "User",
        foreign_keys=[analyst_id]
    )

    note = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<AnalystNote {self.id} Incident:{self.incident_id}>"