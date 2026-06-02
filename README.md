# testFS

Test Flask project for clients, products, and orders.

The project has a REST API and a small HTML UI. Orders belong to clients and contain products. Order totals are calculated on the backend from product prices and quantities.

## Stack

- Backend: Flask + SQLAlchemy
- Frontend: Jinja2 Templates + Bootstrap + TypeScript
- Database: SQLite
- Tests: pytest
- Environment: python-dotenv

## Implemented functionality

- Create clients through UI and API.
- Create products through UI and API.
- Create orders through UI and API.
- View client orders through API.
- View clients, products, and orders in the browser.
- View order details in the browser.
- Calculate order totals automatically on the backend.
- Validate basic business rules.
- Use a simple HTML wrapper for working without Postman.
- Preview order totals with TypeScript on the order creation page.

## Project structure

```text
app/
  models/      SQLAlchemy models
  routes/      HTML and API routes
  services/    business logic
  schemas/     API serializers
  static/      CSS and JavaScript files
  templates/   Jinja2 templates
  utils/       API response helpers
tests/         pytest tests
init_db.py     database initialization script
run.py         application entrypoint
requests.http  API request examples
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

On Linux or macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` if you want to override defaults:

```env
FLASK_ENV=development
APP_ENV=development
SECRET_KEY=change-me
DATABASE_URL=sqlite:///k2_orders.db
```

Create database tables:

```bash
python init_db.py
```

## Run

Start the app:

```bash
python run.py
```

After running the project, open:
http://127.0.0.1:5000/

Health check:

```http
GET http://127.0.0.1:5000/health
```

## HTML UI

```text
GET /                  home page
GET /clients           clients list
GET /clients/create    create client form
GET /products          products list
GET /products/create   create product form
GET /orders            orders list
GET /orders/<id>       order details
GET /orders/create     create order form
```

The UI is built with Jinja2 templates and Bootstrap. It is a simple browser wrapper around the same data model used by the API.

## REST API

The API is available under `/api/*` and returns JSON. You can use `requests.http`, Postman, curl, or another HTTP client.

```http
POST /api/clients
GET /api/clients
GET /api/clients/<client_id>/orders

POST /api/products
GET /api/products

POST /api/orders
```

Example client:

```json
{
  "name": "Test Client",
  "email": "test@example.com",
  "phone": "+380000000000"
}
```

Example product:

```json
{
  "name": "Test Product",
  "sku": "TEST-001",
  "price": "100.00"
}
```

Example order:

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

## TypeScript

- Source file: `app/static/js/orders.ts`
- Browser file: `app/static/js/orders.js`

`orders.js` is connected on the order creation page. It updates the preview total when products or quantities change. The preview is not submitted as the order total; the final amount is calculated on the backend.

## Business rules

- Client email is unique.
- Product SKU is unique.
- Product price must be greater than `0`.
- An order must have an existing client.
- An order must contain at least one product.
- The user does not enter `total_amount`.
- Order totals are calculated on the backend as `product.price * quantity`.

## Tests

Run tests:

```bash
pytest
```

The test config uses an in-memory SQLite database.

## Docker

Build and start the app:

```bash
docker compose up --build
```

Create database tables inside the container:

```bash
docker compose exec web python init_db.py
```
