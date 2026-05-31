from app.models import Product


def test_create_product_success(client):
    response = client.post(
        "/api/products",
        json={
            "name": "Test Product",
            "sku": "TEST-001",
            "price": "100.00",
        },
    )

    response_json = response.get_json()
    data = response_json["data"]

    assert response.status_code == 201
    assert response_json["message"] == "Product created successfully"
    assert data["id"]
    assert data["name"] == "Test Product"
    assert data["sku"] == "TEST-001"
    assert data["price"] == "100.00"
    assert data["created_at"]

    product_from_db = Product.query.filter_by(sku="TEST-001").first()
    assert product_from_db is not None
    assert product_from_db.name == "Test Product"


def test_create_product_price_must_be_greater_than_zero(client):
    for payload in [
        {
            "name": "Bad Product",
            "sku": "BAD-001",
            "price": "0.00",
        },
        {
            "name": "Bad Product",
            "sku": "BAD-002",
            "price": "-10.00",
        },
    ]:
        response = client.post("/api/products", json=payload)
        response_json = response.get_json()

        assert response.status_code == 400
        assert response_json["error"] == "Validation error"
        assert response_json["details"] == "Price must be greater than zero"


def test_create_product_duplicate_sku_returns_conflict(client):
    client.post(
        "/api/products",
        json={
            "name": "First Product",
            "sku": "DUP-001",
            "price": "100.00",
        },
    )

    response = client.post(
        "/api/products",
        json={
            "name": "Second Product",
            "sku": "DUP-001",
            "price": "200.00",
        },
    )

    response_json = response.get_json()

    assert response.status_code == 409
    assert response_json["error"] == "Conflict"
    assert response_json["details"] == "Product with this sku already exists"
