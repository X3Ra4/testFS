import click
from sqlalchemy.exc import IntegrityError

from app.database import db
from app.models import Client


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
