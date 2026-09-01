from datetime import datetime

from app import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    action = db.Column(
        db.String(100),
        nullable=False
    )

    resource_type = db.Column(
        db.String(50),
        nullable=True
    )

    resource_id = db.Column(
        db.Integer,
        nullable=True
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    source_ip = db.Column(
        db.String(45),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<AuditLog {self.id} {self.action}>"