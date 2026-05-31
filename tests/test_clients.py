from app.models import Client


def test_create_client_success(client):
    response = client.post(
        "/api/clients",
        json={
            "name": "Test Client",
            "email": "test@example.com",
            "phone": "+380000000000",
        },
    )

    response_json = response.get_json()
    data = response_json["data"]

    assert response.status_code == 201
    assert response_json["message"] == "Client created successfully"
    assert data["id"]
    assert data["name"] == "Test Client"
    assert data["email"] == "test@example.com"
    assert data["phone"] == "+380000000000"
    assert data["created_at"]

    client_from_db = Client.query.filter_by(email="test@example.com").first()
    assert client_from_db is not None
    assert client_from_db.name == "Test Client"


def test_create_client_without_name_returns_validation_error(client):
    response = client.post(
        "/api/clients",
        json={
            "email": "no-name@example.com",
            "phone": "+380000000000",
        },
    )

    response_json = response.get_json()

    assert response.status_code == 400
    assert response_json["error"] == "Validation error"
    assert response_json["details"] == "Name is required"


def test_create_client_duplicate_email_returns_conflict(client):
    client.post(
        "/api/clients",
        json={
            "name": "First Client",
            "email": "duplicate@example.com",
            "phone": "+380000000000",
        },
    )

    response = client.post(
        "/api/clients",
        json={
            "name": "Second Client",
            "email": "duplicate@example.com",
            "phone": "+380111111111",
        },
    )

    response_json = response.get_json()

    assert response.status_code == 409
    assert response_json["error"] == "Conflict"
    assert response_json["details"] == "Client with this email already exists"
