from datetime import datetime

from app import db


class Incident(db.Model):
    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)

    description = db.Column(db.Text, nullable=True)

    severity = db.Column(
        db.String(20),
        nullable=False,
        default="medium"
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="open"
    )

    assigned_to = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    resolved_at = db.Column(
        db.DateTime,
        nullable=True
    )

    resolution = db.Column(
        db.Text,
        nullable=True
    )

    def __repr__(self):
        return f"<Incident {self.id} {self.title}>"