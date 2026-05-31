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
            raise ClientNotFoundError("Client not found")

        if not items_data:
            raise ValueError("Order must contain at least one item")

        order_items = []
        total_amount = Decimal("0.00")

        for item_data in items_data:
            if not isinstance(item_data, dict):
                raise ValueError("Each order item must be an object")

            product_id = item_data.get("product_id")

            if product_id is None:
                raise ValueError("Product id is required")

            product = db.session.get(Product, product_id)

            if not product:
                raise ProductNotFoundError(f"Product with id {product_id} not found")

            quantity = item_data.get("quantity")

            if quantity is None:
                raise ValueError("Quantity is required")

            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                raise ValueError("Quantity must be a positive integer")

            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero")

            unit_price = Decimal(product.price)
            total_price = unit_price * quantity
            total_amount += total_price

            order_items.append(
                OrderItem(
                    product_id=product.id,
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
