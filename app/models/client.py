from datetime import datetime, timezone

from app.database import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    phone = db.Column(db.String(30), nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    orders = db.relationship(
        "Order",
        back_populates="client",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Client id={self.id} email={self.email}>"
