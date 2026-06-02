# testFS

Flask REST API for managing clients, products, and orders.

Orders belong to clients, orders contain products, and order totals are calculated on the backend from product prices and quantities.

## Stack

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- pytest
- python-dotenv

## Project Structure

```text
app/
  models/      SQLAlchemy models
  routes/      HTTP endpoints
  services/    business logic
  schemas/     response serialization
  static/      minimal frontend assets
  templates/   minimal frontend page
  utils/       API response helpers
tests/         pytest tests
init_db.py     database initialization script
run.py         application entrypoint
requests.http  ready-to-run HTTP examples
Dockerfile
docker-compose.yml
requirements.txt
.env.example
```

## Installation

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Activate it on Linux/Mac:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment

Create `.env` from `.env.example`.

Example:

```env
FLASK_ENV=development
APP_ENV=development
SECRET_KEY=change-me
DATABASE_URL=sqlite:///k2_orders.db
```

The app selects its config by `APP_ENV`. `FLASK_ENV` is included for Flask tooling compatibility. If `DATABASE_URL` is not set, the app uses local SQLite by default. Tests use the `testing` config with a separate in-memory SQLite database.

## Database

Create the SQLite database tables:

```bash
python init_db.py
```

This command creates the configured SQLite database and all SQLAlchemy tables.

## Run

Start the application:

```bash
python run.py
```

Health check:

```http
GET http://127.0.0.1:5000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## HTML Page

A simple HTML page is available at:

```text
http://127.0.0.1:5000/
```

The page is only for manual API checks. The main project interface is the REST API.

## Frontend TypeScript

- TypeScript logic for the order total preview is in `app/static/js/orders.ts`.
- The compiled browser file is `app/static/js/orders.js`.
- The order creation page loads `orders.js`, not `orders.ts`.
- The frontend preview is only a convenience for the user.
- The final order total is always calculated on the backend from order items.

## Docker

Build and start the application with Docker:

```bash
docker compose up --build
```

Create database tables inside the running container:

```bash
docker compose exec web python init_db.py
```

Check the application:

```bash
curl http://127.0.0.1:5000/health
```

## Endpoints

Clients:

```http
POST /api/clients
GET /api/clients
GET /api/clients/<id>
GET /api/clients/<client_id>/orders
```

Products:

```http
POST /api/products
GET /api/products
GET /api/products/<id>
```

Orders:

```http
POST /api/orders
GET /api/orders/<id>
```

## Request Examples

Ready-to-run HTTP examples are available in `requests.http`. They can be executed with VS Code REST Client or a compatible HTTP client.

`frontend-example.ts` contains a small TypeScript integration example with API response types and a typed `createOrder()` call.

Create a client:

```json
{
  "name": "Test Client",
  "email": "test@example.com",
  "phone": "+380000000000"
}
```

Create a product:

```json
{
  "name": "Test Product",
  "sku": "TEST-001",
  "price": "100.00"
}
```

Create an order:

```json
{
  "client_id": 1,
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ]
}
```

## Success Response Format

```json
{
  "data": {},
  "message": "Success message"
}
```

Create endpoints return `201`. Read endpoints return `200`.

## Error Response Format

```json
{
  "error": "Validation error",
  "details": "Details text"
}
```

Validation errors return `400`, conflicts return `409`, and missing resources return `404`.

## Business Rules

- An order cannot be created without an existing client.
- An order must contain at least one product.
- `total_amount` is not accepted from the user.
- Order totals are calculated on the backend as `product.price * quantity`.
- Product price must be greater than `0`.
- Client email is unique.
- Product SKU is unique.
- Money values are returned as strings with two decimal places.

## Tests

Run tests:

```bash
pytest
```

Tests use `create_app("testing")` and an in-memory SQLite database, so development data is not touched.

## Architecture

- `models/` contains SQLAlchemy models.
- `routes/` contains Flask blueprints and HTTP endpoints.
- `services/` contains business logic, including order creation.
- `schemas/` contains serializers for API response data.
- `utils/` contains response helpers for success and error formats.
- `tests/` contains pytest coverage for health, clients, products, and orders.
