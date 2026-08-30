from datetime import datetime

from app import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)

    alert_type = db.Column(db.String(100), nullable=False)

    severity = db.Column(
        db.String(20),
        nullable=False,
        default="medium"
    )

    description = db.Column(db.Text, nullable=False)

    source_ip = db.Column(db.String(45), nullable=True)

    detection_rule = db.Column(db.String(100), nullable=False)

    status = db.Column(
        db.String(30),
        nullable=False,
        default="new"
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

    def __repr__(self):
        return f"<Alert {self.id} {self.alert_type}>"