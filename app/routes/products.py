from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Product


products_bp = Blueprint("products", __name__)


def normalize_required_string(value):
    if not isinstance(value, str):
        return None

    value = value.strip()
    return value or None


def parse_price(value):
    if value is None:
        return None, "price is required"

    try:
        price = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None, "price must be a valid number"

    if price <= 0:
        return None, "price must be greater than zero"

    return price, None


@products_bp.post("")
def create_product():
    if not request.is_json:
        return jsonify({"error": "request body must be JSON"}), 400

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "request body must be JSON"}), 400

    name = normalize_required_string(data.get("name"))

    if not name:
        return jsonify({"error": "name is required"}), 400

    sku = normalize_required_string(data.get("sku"))

    if not sku:
        return jsonify({"error": "sku is required"}), 400

    price, price_error = parse_price(data.get("price"))

    if price_error:
        return jsonify({"error": price_error}), 400

    existing_product = Product.query.filter_by(sku=sku).first()

    if existing_product:
        return jsonify({"error": "product with this sku already exists"}), 409

    product = Product(name=name, sku=sku, price=price)
    db.session.add(product)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "product with this sku already exists"}), 409
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 400

    return jsonify(product.to_dict()), 201


@products_bp.get("")
def get_products():
    products = Product.query.order_by(Product.id).all()
    return jsonify([product.to_dict() for product in products]), 200


@products_bp.get("/<int:product_id>")
def get_product(product_id):
    product = db.session.get(Product, product_id)

    if not product:
        return jsonify({"error": "product not found"}), 404

    return jsonify(product.to_dict()), 200
