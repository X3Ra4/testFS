from flask import Blueprint, request

from app.database import db
from app.models import Order
from app.schemas import serialize_order
from app.services.order_service import (
    ClientNotFoundError,
    ProductNotFoundError,
    create_order,
)
from app.utils.responses import error_response, success_response


orders_bp = Blueprint("orders", __name__)


@orders_bp.post("")
def create_order_endpoint():
    if not request.is_json:
        return error_response("Validation error", "Request body must be JSON", 400)

    data = request.get_json(silent=True)

    if not data:
        return error_response("Validation error", "Request body must be JSON", 400)

    client_id = data.get("client_id")

    if client_id is None:
        return error_response("Validation error", "Client id is required", 400)

    items = data.get("items")

    if items is None:
        return error_response(
            "Validation error",
            "Order must contain at least one item",
            400,
        )

    if not isinstance(items, list):
        return error_response(
            "Validation error",
            "Order must contain at least one item",
            400,
        )

    if not items:
        return error_response(
            "Validation error",
            "Order must contain at least one item",
            400,
        )

    try:
        order = create_order(client_id, items)
    except (ClientNotFoundError, ProductNotFoundError) as exc:
        return error_response("Not found", str(exc), 404)
    except ValueError as exc:
        return error_response("Validation error", str(exc), 400)

    return success_response(
        serialize_order(order),
        "Order created successfully",
        201,
    )


@orders_bp.get("/<int:order_id>")
def get_order(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        return error_response("Not found", "Order not found", 404)

    return success_response(
        serialize_order(order),
        "Order retrieved successfully",
        200,
    )
