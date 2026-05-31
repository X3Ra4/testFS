def create_client(client, email):
    response = client.post(
        "/api/clients",
        json={
            "name": "Test Client",
            "email": email,
        },
    )
    return response.get_json()["data"]


def create_product(client, sku):
    response = client.post(
        "/api/products",
        json={
            "name": "Test Product",
            "sku": sku,
            "price": "100.00",
        },
    )
    return response.get_json()["data"]


def create_order(client, client_id, product_id):
    response = client.post(
        "/api/orders",
        json={
            "client_id": client_id,
            "items": [
                {
                    "product_id": product_id,
                    "quantity": 1,
                }
            ],
        },
    )
    return response.get_json()["data"]


def test_get_client_orders_returns_only_that_clients_orders(client):
    first_client = create_client(client, "client-1@example.com")
    second_client = create_client(client, "client-2@example.com")
    product = create_product(client, "CLIENT-ORDERS-PRODUCT")
    first_order = create_order(client, first_client["id"], product["id"])
    second_order = create_order(client, second_client["id"], product["id"])

    response = client.get(f"/api/clients/{first_client['id']}/orders")
    response_json = response.get_json()
    data = response_json["data"]
    order_ids = {order["id"] for order in data}

    assert response.status_code == 200
    assert isinstance(data, list)
    assert first_order["id"] in order_ids
    assert second_order["id"] not in order_ids
    assert all(order["client_id"] == first_client["id"] for order in data)


def test_get_client_orders_returns_empty_list_for_client_without_orders(client):
    created_client = create_client(client, "client-without-orders@example.com")

    response = client.get(f"/api/clients/{created_client['id']}/orders")
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["data"] == []


def test_get_client_orders_for_unknown_client_returns_not_found(client):
    response = client.get("/api/clients/999999/orders")
    response_json = response.get_json()

    assert response.status_code == 404
    assert response_json["error"] == "Not found"
    assert response_json["details"] == "Client not found"
