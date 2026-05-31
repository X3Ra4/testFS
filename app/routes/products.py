from decimal import Decimal, InvalidOperation

from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Product
from app.schemas import serialize_product
from app.utils.responses import error_response, success_response


products_bp = Blueprint("products", __name__)


def normalize_required_string(value):
    if not isinstance(value, str):
        return None

    value = value.strip()
    return value or None


def parse_price(value):
    if value is None:
        return None, "Price is required"

    try:
        price = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None, "Price must be a valid number"

    if price <= 0:
        return None, "Price must be greater than zero"

    return price, None


@products_bp.post("")
def create_product():
    if not request.is_json:
        return error_response("Validation error", "Request body must be JSON", 400)

    data = request.get_json(silent=True)

    if not data:
        return error_response("Validation error", "Request body must be JSON", 400)

    name = normalize_required_string(data.get("name"))

    if not name:
        return error_response("Validation error", "Name is required", 400)

    sku = normalize_required_string(data.get("sku"))

    if not sku:
        return error_response("Validation error", "Sku is required", 400)

    price, price_error = parse_price(data.get("price"))

    if price_error:
        return error_response("Validation error", price_error, 400)

    existing_product = Product.query.filter_by(sku=sku).first()

    if existing_product:
        return error_response(
            "Conflict",
            "Product with this sku already exists",
            409,
        )

    product = Product(name=name, sku=sku, price=price)
    db.session.add(product)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error_response(
            "Conflict",
            "Product with this sku already exists",
            409,
        )
    except ValueError as exc:
        db.session.rollback()
        return error_response("Validation error", str(exc), 400)

    return success_response(
        serialize_product(product),
        "Product created successfully",
        201,
    )


@products_bp.get("")
def get_products():
    products = Product.query.order_by(Product.id).all()
    return success_response(
        [serialize_product(product) for product in products],
        "Products retrieved successfully",
        200,
    )


@products_bp.get("/<int:product_id>")
def get_product(product_id):
    product = db.session.get(Product, product_id)

    if not product:
        return error_response("Not found", "Product not found", 404)

    return success_response(
        serialize_product(product),
        "Product retrieved successfully",
        200,
    )
