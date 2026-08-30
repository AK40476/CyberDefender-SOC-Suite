from datetime import datetime

from app import db


class SecurityLog(db.Model):
    __tablename__ = "security_logs"

    id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(db.DateTime, nullable=False)

    source_ip = db.Column(db.String(45), nullable=True)
    destination_ip = db.Column(db.String(45), nullable=True)

    username = db.Column(db.String(80), nullable=True)

    event_type = db.Column(db.String(50), nullable=False)

    status = db.Column(db.String(30), nullable=True)

    message = db.Column(db.Text, nullable=False)

    source = db.Column(db.String(50), nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<SecurityLog {self.id} {self.event_type}>"