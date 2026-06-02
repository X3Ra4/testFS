from decimal import Decimal, InvalidOperation

from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Client, Product


pages_bp = Blueprint("pages", __name__)


@pages_bp.get("/")
def index():
    return render_template("index.html")


@pages_bp.get("/clients")
def clients_list():
    clients = Client.query.order_by(Client.id).all()
    return render_template("clients/list.html", clients=clients)


@pages_bp.route("/clients/create", methods=["GET", "POST"])
def clients_create():
    form_data = {
        "name": "",
        "email": "",
        "phone": "",
    }
    errors = []

    if request.method == "POST":
        form_data = {
            "name": request.form.get("name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
        }

        if not form_data["name"]:
            errors.append("Имя обязательно")

        if not form_data["email"]:
            errors.append("Email обязателен")

        email = form_data["email"].lower()
        if email:
            existing_client = Client.query.filter(func.lower(Client.email) == email).first()
            if existing_client:
                errors.append("Клиент с таким email уже существует")

        if not errors:
            client = Client(
                name=form_data["name"],
                email=email,
                phone=form_data["phone"] or None,
            )
            db.session.add(client)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errors.append("Клиент с таким email уже существует")
            else:
                return redirect(url_for("pages.clients_list"))

    return render_template(
        "clients/create.html",
        errors=errors,
        form_data=form_data,
    )


@pages_bp.get("/products")
def products_list():
    products = Product.query.order_by(Product.id).all()
    return render_template("products/list.html", products=products)


@pages_bp.route("/products/create", methods=["GET", "POST"])
def products_create():
    form_data = {
        "name": "",
        "sku": "",
        "price": "",
    }
    errors = []

    if request.method == "POST":
        form_data = {
            "name": request.form.get("name", "").strip(),
            "sku": request.form.get("sku", "").strip(),
            "price": request.form.get("price", "").strip(),
        }

        if not form_data["name"]:
            errors.append("Название обязательно")

        if not form_data["sku"]:
            errors.append("SKU обязателен")

        price = None
        if not form_data["price"]:
            errors.append("Цена обязательна")
        else:
            try:
                price = Decimal(form_data["price"])
            except (InvalidOperation, ValueError):
                errors.append("Цена должна быть числом")
            else:
                if price <= 0:
                    errors.append("Цена должна быть больше 0")

        if form_data["sku"]:
            existing_product = Product.query.filter_by(sku=form_data["sku"]).first()
            if existing_product:
                errors.append("Товар с таким SKU уже существует")

        if not errors:
            product = Product(
                name=form_data["name"],
                sku=form_data["sku"],
                price=price,
            )
            db.session.add(product)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errors.append("Товар с таким SKU уже существует")
            except ValueError:
                db.session.rollback()
                errors.append("Цена должна быть больше 0")
            else:
                return redirect(url_for("pages.products_list"))

    return render_template(
        "products/create.html",
        errors=errors,
        form_data=form_data,
    )
