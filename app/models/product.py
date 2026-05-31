from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import validates

from app.database import db


class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (
        db.CheckConstraint("price > 0", name="check_product_price_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    order_items = db.relationship("OrderItem", back_populates="product")

    @validates("price")
    def validate_price(self, key, value):
        price = Decimal(value)

        if price <= 0:
            raise ValueError("Product price must be greater than zero.")

        return price

    def __repr__(self):
        return f"<Product id={self.id} sku={self.sku} price={self.price}>"
