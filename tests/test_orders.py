from app.database import db
from app.models import Client, Order, Product


def create_client(email="order-client@example.com"):
    client = Client(name="Order Client", email=email)
    db.session.add(client)
    db.session.commit()
    return client


def create_product(sku="ORDER-PRODUCT-001", price="100.00"):
    product = Product(name="Order Product", sku=sku, price=price)
    db.session.add(product)
    db.session.commit()
    return product


def test_create_order_success(client):
    created_client = create_client()
    product = create_product(price="100.00")

    response = client.post(
        "/api/orders",
        json={
            "client_id": created_client.id,
            "items": [
                {
                    "product_id": product.id,
                    "quantity": 2,
                }
            ],
        },
    )

    response_json = response.get_json()
    data = response_json["data"]
    item = data["items"][0]

    assert response.status_code == 201
    assert data["id"]
    assert data["client_id"] == created_client.id
    assert data["items"]
    assert data["total_amount"] == "200.00"
    assert data["created_at"]
    assert item["product_id"] == product.id
    assert item["quantity"] == 2
    assert item["unit_price"] == "100.00"
    assert item["line_total"] == "200.00"

    order_from_db = db.session.get(Order, data["id"])
    assert order_from_db is not None
    assert order_from_db.client_id == created_client.id
    assert len(order_from_db.items) == 1


def test_create_order_total_amount_is_calculated_on_backend(client):
    created_client = create_client(email="calculation@example.com")
    first_product = create_product(sku="ORDER-PRODUCT-001", price="100.00")
    second_product = create_product(sku="ORDER-PRODUCT-002", price="50.00")

    response = client.post(
        "/api/orders",
        json={
            "client_id": created_client.id,
            "total_amount": "999999.00",
            "items": [
                {"product_id": first_product.id, "quantity": 2},
                {"product_id": second_product.id, "quantity": 3},
            ],
        },
    )

    data = response.get_json()["data"]

    assert response.status_code == 201
    assert data["total_amount"] == "350.00"
    assert data["total_amount"] != "999999.00"


def test_create_order_without_existing_client_returns_not_found(client):
    product = create_product()
    orders_before = Order.query.count()

    response = client.post(
        "/api/orders",
        json={
            "client_id": 999999,
            "items": [{"product_id": product.id, "quantity": 2}],
        },
    )

    response_json = response.get_json()

    assert response.status_code == 404
    assert response_json["error"] == "Not found"
    assert response_json["details"] == "Client not found"
    assert Order.query.count() == orders_before


def test_create_order_without_items_returns_validation_error(client):
    created_client = create_client()
    orders_before = Order.query.count()

    response = client.post(
        "/api/orders",
        json={
            "client_id": created_client.id,
            "items": [],
        },
    )

    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json["error"] == "Validation error"
    assert response_json["details"] == "Order must contain at least one item"
    assert Order.query.count() == orders_before
