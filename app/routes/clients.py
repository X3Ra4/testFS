from flask import Blueprint, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Client
from app.schemas import serialize_client, serialize_order
from app.utils.responses import error_response, success_response


clients_bp = Blueprint("clients", __name__)


def normalize_required_string(value):
    if not isinstance(value, str):
        return None

    value = value.strip()
    return value or None


def normalize_optional_string(value):
    if value is None:
        return None

    if not isinstance(value, str):
        return value

    value = value.strip()
    return value or None


@clients_bp.post("")
def create_client():
    if not request.is_json:
        return error_response("Validation error", "Request body must be JSON", 400)

    data = request.get_json(silent=True)

    if not data:
        return error_response("Validation error", "Request body must be JSON", 400)

    name = normalize_required_string(data.get("name"))

    if not name:
        return error_response("Validation error", "Name is required", 400)

    email = normalize_required_string(data.get("email"))

    if not email:
        return error_response("Validation error", "Email is required", 400)

    email = email.lower()
    phone = normalize_optional_string(data.get("phone"))

    if phone is not None and not isinstance(phone, str):
        return error_response("Validation error", "Phone must be a string", 400)

    existing_client = Client.query.filter(func.lower(Client.email) == email).first()

    if existing_client:
        return error_response(
            "Conflict",
            "Client with this email already exists",
            409,
        )

    client = Client(name=name, email=email, phone=phone)
    db.session.add(client)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error_response(
            "Conflict",
            "Client with this email already exists",
            409,
        )

    return success_response(
        serialize_client(client),
        "Client created successfully",
        201,
    )


@clients_bp.get("")
def get_clients():
    clients = Client.query.order_by(Client.id).all()
    return success_response(
        [serialize_client(client) for client in clients],
        "Clients retrieved successfully",
        200,
    )


@clients_bp.get("/<int:client_id>")
def get_client(client_id):
    client = db.session.get(Client, client_id)

    if not client:
        return error_response("Not found", "Client not found", 404)

    return success_response(
        serialize_client(client),
        "Client retrieved successfully",
        200,
    )


@clients_bp.get("/<int:client_id>/orders")
def get_client_orders(client_id):
    client = db.session.get(Client, client_id)

    if not client:
        return error_response("Not found", "Client not found", 404)

    orders = sorted(client.orders, key=lambda order: order.id)
    return success_response(
        [serialize_order(order) for order in orders],
        "Client orders retrieved successfully",
        200,
    )
