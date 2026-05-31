# testFS

Minimal Flask project for a test assignment.

## Configuration

Application settings are loaded from `.env`.

Available variables:

```env
APP_ENV=development
SECRET_KEY=change-me
DATABASE_URL=sqlite:///app.db
```

If `APP_ENV` is not set, the app uses `development` mode. If `DATABASE_URL` is not set, the app uses local SQLite at `sqlite:///app.db`. For `APP_ENV=testing`, the app uses a separate in-memory SQLite database by default.

## Setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```powershell
python run.py
```

The application starts at:

```text
http://127.0.0.1:5000
```

## Database

Create database tables explicitly:

```powershell
flask --app run init-db
```

Create a test client:

```powershell
flask --app run seed-client
```

The seed command creates this client if it does not already exist:

```text
name: Test Client
email: test@example.com
phone: +380000000000
```

Check that the client was saved:

```powershell
python -c "from app import create_app; from app.models import Client; app = create_app(); app.app_context().push(); print(Client.query.filter_by(email='test@example.com').first())"
```

Create a test product:

```powershell
flask --app run seed-product
```

The seed command creates this product if it does not already exist:

```text
name: Test Product
sku: TEST-001
price: 100.00
```

Check that the product was saved and the price keeps two decimal places:

```powershell
python -c "from app import create_app; from app.models import Product; app = create_app(); app.app_context().push(); product = Product.query.filter_by(sku='TEST-001').first(); print(product); print(product.price)"
```

Check that a negative price is rejected:

```powershell
python -c "from app.models import Product; Product(name='Bad Product', sku='BAD-001', price='-10.00')"
```

Create a test order for the test client:

```powershell
flask --app run seed-order
```

The seed command creates the test client and test products first if they do not exist, then creates an order with two items:

```text
client: test@example.com
items:
  TEST-001 x 2
  TEST-002 x 1
```

Check that the order is linked to the client:

```powershell
python -c "from app import create_app; from app.models import Client, Order; app = create_app(); app.app_context().push(); order = Order.query.first(); print(order); print(order.client); print(Client.query.filter_by(email='test@example.com').first().orders)"
```

Check that one order has multiple products and each item stores its historical price:

```powershell
python -c "from app import create_app; from app.models import Order; app = create_app(); app.app_context().push(); order = Order.query.order_by(Order.id.desc()).first(); print(order); [print(item, item.product, item.unit_price, item.total_price) for item in order.items]"
```

For each item, `total_price` is calculated from `unit_price * quantity`.

Create an order through the service layer:

```powershell
python -c "from app import create_app; from app.services.order_service import create_order; app = create_app(); app.app_context().push(); order = create_order(1, [{'product_id': 1, 'quantity': 2}]); print(order); print(order.items)"
```

Check that a negative order amount is rejected:

```powershell
python -c "from app.models import Order; Order(client_id=1, total_amount='-10.00')"
```

Check that an invalid order item is rejected:

```powershell
python -c "from app.models import OrderItem; OrderItem(order_id=1, product_id=1, quantity=0, unit_price='100.00')"
```

## Clients API

Create a client:

```powershell
Invoke-RestMethod -Method Post -ContentType "application/json" -Uri http://127.0.0.1:5000/api/clients -Body '{"name":"Test Client","email":"test@example.com","phone":"+380000000000"}'
```

Get all clients:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/clients
```

Get one client:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/clients/1
```

Get orders for one client:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/clients/1/orders
```

Client JSON format:

```json
{
  "id": 1,
  "name": "Test Client",
  "email": "test@example.com",
  "phone": "+380000000000",
  "created_at": "2026-05-31T12:00:00"
}
```

Missing `name` or `email` returns `400`. Reusing an existing email returns `409`. Requesting an unknown client returns `404`.
`name`, `email`, and `phone` are stripped before saving. Empty strings and whitespace-only values are rejected for `name` and `email`. Email is stored in lowercase, so duplicate checks are case-insensitive.

## Products API

Create a product:

```powershell
Invoke-RestMethod -Method Post -ContentType "application/json" -Uri http://127.0.0.1:5000/api/products -Body '{"name":"Test Product","sku":"TEST-001","price":"100.00"}'
```

Get all products:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/products
```

Get one product:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/products/1
```

Product JSON format:

```json
{
  "id": 1,
  "name": "Test Product",
  "sku": "TEST-001",
  "price": "100.00",
  "created_at": "2026-05-31T12:00:00"
}
```

`name` and `sku` are stripped before saving. Empty strings and whitespace-only values are rejected. `price` is parsed as `Decimal`, must be greater than zero, and is returned as a string with two decimal places. Reusing an existing `sku` returns `409`. Requesting an unknown product returns `404`.

## Orders API

Create an order:

```powershell
Invoke-RestMethod -Method Post -ContentType "application/json" -Uri http://127.0.0.1:5000/api/orders -Body '{"client_id":1,"items":[{"product_id":1,"quantity":2}]}'
```

Get one order:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/api/orders/1
```

Order JSON format:

```json
{
  "id": 1,
  "client_id": 1,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "quantity": 2,
      "unit_price": "100.00",
      "total_price": "200.00"
    }
  ],
  "total_amount": "200.00",
  "created_at": "2026-05-31T12:00:00"
}
```

`total_amount` is not accepted from the request. It is calculated on the backend from product prices and item quantities.

## Error Format

API errors use one JSON format:

```json
{
  "error": "Validation error",
  "details": "Name is required"
}
```

Validation errors return `400`, conflicts return `409`, and missing resources return `404`.

## Success Format

API success responses use one JSON format:

```json
{
  "data": {},
  "message": "Success"
}
```

Create endpoints return `201`, and read endpoints return `200`.

## Serialization

API data serialization is centralized in `app/schemas/serializers.py`.

## Health Check

Check the health endpoint:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/health
```

Expected response:

```json
{"status":"ok"}
```
