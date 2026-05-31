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

## Health Check

Check the health endpoint:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5000/health
```

Expected response:

```json
{"status":"ok"}
```
