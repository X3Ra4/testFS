from flask import Blueprint, jsonify, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Client


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
        return jsonify({"error": "request body must be JSON"}), 400

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "request body must be JSON"}), 400

    name = normalize_required_string(data.get("name"))

    if not name:
        return jsonify({"error": "name is required"}), 400

    email = normalize_required_string(data.get("email"))

    if not email:
        return jsonify({"error": "email is required"}), 400

    email = email.lower()
    phone = normalize_optional_string(data.get("phone"))

    if phone is not None and not isinstance(phone, str):
        return jsonify({"error": "phone must be a string"}), 400

    existing_client = Client.query.filter(func.lower(Client.email) == email).first()

    if existing_client:
        return jsonify({"error": "client with this email already exists"}), 409

    client = Client(name=name, email=email, phone=phone)
    db.session.add(client)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "client with this email already exists"}), 409

    return jsonify(client.to_dict()), 201


@clients_bp.get("")
def get_clients():
    clients = Client.query.order_by(Client.id).all()
    return jsonify([client.to_dict() for client in clients]), 200


@clients_bp.get("/<int:client_id>")
def get_client(client_id):
    client = db.session.get(Client, client_id)

    if not client:
        return jsonify({"error": "client not found"}), 404

    return jsonify(client.to_dict()), 200
