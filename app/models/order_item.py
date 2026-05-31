from decimal import Decimal

from sqlalchemy import event
from sqlalchemy.orm import validates

from app.database import db


class OrderItem(db.Model):
    __tablename__ = "order_items"
    __table_args__ = (
        db.CheckConstraint("quantity > 0", name="check_order_item_quantity_positive"),
        db.CheckConstraint("unit_price >= 0", name="check_order_item_unit_price_non_negative"),
        db.CheckConstraint("line_total >= 0", name="check_order_item_line_total_non_negative"),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)

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

    def calculate_line_total(self):
        self.line_total = Decimal(self.unit_price) * self.quantity

    def __repr__(self):
        return (
            f"<OrderItem id={self.id} order_id={self.order_id} "
            f"product_id={self.product_id} quantity={self.quantity} "
            f"line_total={self.line_total}>"
        )


@event.listens_for(OrderItem, "before_insert")
@event.listens_for(OrderItem, "before_update")
def calculate_order_item_line_total(mapper, connection, target):
    target.calculate_line_total()
