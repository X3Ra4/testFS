from flask import Blueprint, jsonify, request

from app.database import db
from app.models import Order
from app.services.order_service import (
    ClientNotFoundError,
    ProductNotFoundError,
    create_order,
)


orders_bp = Blueprint("orders", __name__)


@orders_bp.post("")
def create_order_endpoint():
    if not request.is_json:
        return jsonify({"error": "request body must be JSON"}), 400

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "request body must be JSON"}), 400

    client_id = data.get("client_id")

    if client_id is None:
        return jsonify({"error": "client_id is required"}), 400

    items = data.get("items")

    if items is None:
        return jsonify({"error": "order must contain at least one item"}), 400

    if not isinstance(items, list):
        return jsonify({"error": "order must contain at least one item"}), 400

    if not items:
        return jsonify({"error": "order must contain at least one item"}), 400

    try:
        order = create_order(client_id, items)
    except (ClientNotFoundError, ProductNotFoundError) as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(order.to_dict()), 201


@orders_bp.get("/<int:order_id>")
def get_order(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return jsonify({"error": "order not found"}), 404

    return jsonify(order.to_detail_dict()), 200
