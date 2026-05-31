from decimal import Decimal

from app.database import db
from app.models import Client, Order, OrderItem, Product


class OrderServiceError(ValueError):
    pass


class ClientNotFoundError(OrderServiceError):
    pass


class ProductNotFoundError(OrderServiceError):
    pass


def create_order(client_id, items_data):
    try:
        client = db.session.get(Client, client_id)

        if not client:
            raise ClientNotFoundError("client not found")

        if not items_data:
            raise ValueError("order must contain at least one item")

        order_items = []
        total_amount = Decimal("0.00")

        for item_data in items_data:
            if not isinstance(item_data, dict):
                raise ValueError("each order item must be an object")

            product_id = item_data.get("product_id")

            if product_id is None:
                raise ValueError("product_id is required")

            product = db.session.get(Product, product_id)

            if not product:
                raise ProductNotFoundError(f"product with id {product_id} not found")

            quantity = item_data.get("quantity")

            if quantity is None:
                raise ValueError("quantity is required")

            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                raise ValueError("quantity must be a positive integer")

            if quantity <= 0:
                raise ValueError("quantity must be greater than zero")

            unit_price = Decimal(product.price)
            total_price = unit_price * quantity
            total_amount += total_price

            order_items.append(
                OrderItem(
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                )
            )

        order = Order(
            client_id=client.id,
            total_amount=total_amount,
            items=order_items,
        )

        db.session.add(order)
        db.session.commit()
        return order
    except Exception:
        db.session.rollback()
        raise
