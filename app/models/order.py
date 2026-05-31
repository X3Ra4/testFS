from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import validates

from app.database import db


class Order(db.Model):
    __tablename__ = "orders"
    __table_args__ = (
        db.CheckConstraint("total_amount >= 0", name="check_order_total_non_negative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    client = db.relationship("Client", back_populates="orders")
    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    @validates("total_amount")
    def validate_total_amount(self, key, value):
        total_amount = Decimal(value)

        if total_amount < 0:
            raise ValueError("Order total_amount cannot be negative.")

        return total_amount

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "items": [item.to_dict() for item in self.items],
            "total_amount": f"{self.total_amount:.2f}",
            "created_at": self.created_at.isoformat(),
        }

    def to_detail_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "items": [item.to_detail_dict() for item in self.items],
            "total_amount": f"{self.total_amount:.2f}",
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return (
            f"<Order id={self.id} client_id={self.client_id} "
            f"total_amount={self.total_amount}>"
        )
