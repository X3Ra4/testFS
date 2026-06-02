from flask import Blueprint, redirect, render_template, request, url_for
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Client


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
