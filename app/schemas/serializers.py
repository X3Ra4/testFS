def format_money(value):
    return f"{value:.2f}"


def serialize_client(client):
    return {
        "id": client.id,
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "created_at": client.created_at.isoformat(),
    }


def serialize_product(product):
    return {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "price": format_money(product.price),
        "created_at": product.created_at.isoformat(),
    }


def serialize_order_item(item):
    return {
        "id": item.id,
        "product_id": item.product_id,
        "product_name": item.product.name,
        "sku": item.product.sku,
        "unit_price": format_money(item.unit_price),
        "quantity": item.quantity,
        "line_total": format_money(item.total_price),
    }


def serialize_order(order):
    return {
        "id": order.id,
        "client_id": order.client_id,
        "items": [serialize_order_item(item) for item in order.items],
        "total_amount": format_money(order.total_amount),
        "created_at": order.created_at.isoformat(),
    }
