from datetime import datetime

from app import db


class Evidence(db.Model):
    __tablename__ = "evidence"

    id = db.Column(db.Integer, primary_key=True)

    incident_id = db.Column(
        db.Integer,
        db.ForeignKey("incidents.id"),
        nullable=False
    )

    evidence_type = db.Column(
        db.String(50),
        nullable=False
    )

    title = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    file_path = db.Column(
        db.String(500),
        nullable=True
    )

    hash_value = db.Column(
        db.String(128),
        nullable=True
    )

    collected_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    collected_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Evidence {self.id} {self.title}>"