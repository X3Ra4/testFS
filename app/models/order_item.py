from decimal import Decimal

from sqlalchemy import event
from sqlalchemy.orm import validates

from app.database import db


class OrderItem(db.Model):
    __tablename__ = "order_items"
    __table_args__ = (
        db.CheckConstraint("quantity > 0", name="check_order_item_quantity_positive"),
        db.CheckConstraint("unit_price >= 0", name="check_order_item_unit_price_non_negative"),
        db.CheckConstraint("total_price >= 0", name="check_order_item_total_price_non_negative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")

    @validates("quantity")
    def validate_quantity(self, key, value):
        if value <= 0:
            raise ValueError("Order item quantity must be greater than zero.")

        return value

    @validates("unit_price")
    def validate_unit_price(self, key, value):
        unit_price = Decimal(value)

        if unit_price < 0:
            raise ValueError("Order item unit_price cannot be negative.")

        return unit_price

    def calculate_total_price(self):
        self.total_price = Decimal(self.unit_price) * self.quantity

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": f"{self.unit_price:.2f}",
            "total_price": f"{self.total_price:.2f}",
        }

    def to_detail_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name,
            "sku": self.product.sku,
            "unit_price": f"{self.unit_price:.2f}",
            "quantity": self.quantity,
            "line_total": f"{self.total_price:.2f}",
        }

    def __repr__(self):
        return (
            f"<OrderItem id={self.id} order_id={self.order_id} "
            f"product_id={self.product_id} quantity={self.quantity} "
            f"total_price={self.total_price}>"
        )


@event.listens_for(OrderItem, "before_insert")
@event.listens_for(OrderItem, "before_update")
def calculate_order_item_total_price(mapper, connection, target):
    target.calculate_total_price()
