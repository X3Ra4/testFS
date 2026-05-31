from decimal import Decimal

import click
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Client, Order, OrderItem, Product


def register_cli_commands(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("seed-client")
    def seed_client():
        existing_client = Client.query.filter_by(email="test@example.com").first()

        if existing_client:
            click.echo("Test client already exists.")
            return

        client = Client(
            name="Test Client",
            email="test@example.com",
            phone="+380000000000",
        )

        db.session.add(client)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            click.echo("Test client already exists.")
            return

        click.echo("Test client created.")

    @app.cli.command("seed-product")
    def seed_product():
        existing_product = Product.query.filter_by(sku="TEST-001").first()

        if existing_product:
            click.echo("Test product already exists.")
            return

        product = Product(
            name="Test Product",
            sku="TEST-001",
            price="100.00",
        )

        db.session.add(product)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            click.echo("Test product already exists.")
            return

        click.echo("Test product created.")

    @app.cli.command("seed-order")
    def seed_order():
        client = Client.query.filter_by(email="test@example.com").first()

        if not client:
            client = Client(
                name="Test Client",
                email="test@example.com",
                phone="+380000000000",
            )
            db.session.add(client)
            db.session.flush()

        first_product = Product.query.filter_by(sku="TEST-001").first()

        if not first_product:
            first_product = Product(
                name="Test Product",
                sku="TEST-001",
                price="100.00",
            )
            db.session.add(first_product)

        second_product = Product.query.filter_by(sku="TEST-002").first()

        if not second_product:
            second_product = Product(
                name="Second Test Product",
                sku="TEST-002",
                price="50.00",
            )
            db.session.add(second_product)

        db.session.flush()

        first_item_quantity = 2
        second_item_quantity = 1
        total_amount = (
            Decimal(first_product.price) * first_item_quantity
            + Decimal(second_product.price) * second_item_quantity
        )

        order = Order(
            client=client,
            total_amount=total_amount,
            items=[
                OrderItem(
                    product=first_product,
                    quantity=first_item_quantity,
                    unit_price=first_product.price,
                ),
                OrderItem(
                    product=second_product,
                    quantity=second_item_quantity,
                    unit_price=second_product.price,
                ),
            ],
        )

        db.session.add(order)
        db.session.commit()

        click.echo(f"Test order created: {order}")
