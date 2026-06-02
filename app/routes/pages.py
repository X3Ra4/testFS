from decimal import Decimal, InvalidOperation

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Client, Order, Product
from app.services import ClientNotFoundError, ProductNotFoundError, create_order


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
                flash("Клиент успешно создан.", "success")
                return redirect(url_for("pages.clients_list"))

    if errors:
        flash("Проверьте правильность заполнения формы.", "danger")

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
                flash("Товар успешно создан.", "success")
                return redirect(url_for("pages.products_list"))

    if errors:
        flash("Проверьте правильность заполнения формы.", "danger")

    return render_template(
        "products/create.html",
        errors=errors,
        form_data=form_data,
    )


@pages_bp.get("/orders")
def orders_list():
    orders = Order.query.order_by(Order.id).all()
    return render_template("orders/list.html", orders=orders)


@pages_bp.get("/orders/<int:order_id>")
def orders_detail(order_id):
    order = db.session.get(Order, order_id)

    if not order:
        abort(404)

    return render_template("orders/detail.html", order=order)


@pages_bp.route("/orders/create", methods=["GET", "POST"])
def orders_create():
    clients = Client.query.order_by(Client.id).all()
    products = Product.query.order_by(Product.id).all()
    form_data = {
        "client_id": "",
        "items": [
            {"product_id": "", "quantity": ""},
            {"product_id": "", "quantity": ""},
            {"product_id": "", "quantity": ""},
        ],
    }
    errors = []

    if request.method == "POST":
        form_data = {
            "client_id": request.form.get("client_id", "").strip(),
            "items": [],
        }

        for index in range(3):
            form_data["items"].append(
                {
                    "product_id": request.form.get(f"items[{index}][product_id]", "").strip(),
                    "quantity": request.form.get(f"items[{index}][quantity]", "").strip(),
                }
            )

        client_id = None
        if not form_data["client_id"]:
            errors.append("Клиент обязателен")
        else:
            try:
                client_id = int(form_data["client_id"])
            except ValueError:
                errors.append("Клиент выбран неверно")
            else:
                if not db.session.get(Client, client_id):
                    errors.append("Выбранный клиент не найден")

        items_data = []
        selected_product_ids = set()
        duplicate_product = False

        for item in form_data["items"]:
            product_id_value = item["product_id"]
            quantity_value = item["quantity"]

            if not product_id_value and not quantity_value:
                continue

            if not product_id_value:
                errors.append("Выберите товар или оставьте строку пустой")
                continue

            try:
                product_id = int(product_id_value)
            except ValueError:
                errors.append("Товар выбран неверно")
                continue

            if product_id in selected_product_ids:
                duplicate_product = True
                continue

            selected_product_ids.add(product_id)

            if not db.session.get(Product, product_id):
                errors.append("Выбранный товар не найден")
                continue

            if not quantity_value:
                errors.append("Укажите количество для выбранного товара")
                continue

            try:
                quantity = int(quantity_value)
            except ValueError:
                errors.append("Количество должно быть числом больше 0")
                continue

            if quantity <= 0:
                errors.append("Количество должно быть больше 0")
                continue

            items_data.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                }
            )

        if duplicate_product:
            errors.append("Один товар нельзя выбрать несколько раз")

        if not items_data:
            errors.append("Выберите хотя бы один товар")

        if not errors:
            try:
                order = create_order(client_id, items_data)
            except (ClientNotFoundError, ProductNotFoundError) as exc:
                errors.append(str(exc))
            except ValueError as exc:
                errors.append(str(exc))
            else:
                flash("Заказ успешно создан.", "success")
                return redirect(url_for("pages.orders_detail", order_id=order.id))

    if errors:
        flash("Проверьте правильность заполнения формы.", "danger")

    return render_template(
        "orders/create.html",
        clients=clients,
        products=products,
        errors=errors,
        form_data=form_data,
    )
