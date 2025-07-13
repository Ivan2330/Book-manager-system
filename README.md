---


# Book Manager System

A backend system for managing books, authors, and users. Built with FastAPI, async SQLAlchemy, Alembic, and PostgreSQL. Includes JWT authentication, user roles, import/export functionality, and rate limiting.

## warning (ability to make chenges)
some endpoints (only connected with yourself) can work withput superuser, you can get it and test evethyng with is_superuser = true
```http
PATCH /users/make-me-superuser
```

## Requirements

- Python 3.11+
- PostgreSQL
- pip or poetry
- Docker (optional for running PostgreSQL)

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Ivan2330/Book-manager-system.git
cd Book-manager-system
````

### 2. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: .\venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file in the root directory:

```
database_url=""
secret_key=your key
expire_token_minutes=120
algorithm=HS256
```

Replace `your_secret_key_here` with a secure random string and add your postgers url.


## Database Migrations

### Apply migrations

```bash
alembic upgrade head
```

## Run the application

```bash
uvicorn app.main:app --reload
```

Visit Swagger: [http://localhost:8000](http://localhost:8000/docs)

## Features

* JWT authentication with FastAPI Users
* Book management:

  * CRUD operations
  * Filtering, sorting, pagination
  * Random recommendations
  * Import/export (CSV and JSON)
* Author management
* User management and updates
* Rate limiting via `slowapi`

## Available Endpoints (examples)

* `POST /auth/jwt/login` — login
* `POST /auth/register` — register
* `GET /books/` — list books with filters
* `GET /books/recommend` — get random recommendations
* `GET /books/export?format=json|csv` — export books
* `POST /books/import` — import books
* `GET /authors/` — list authors
* `GET /users/` — list users
* `PATCH /users/make-me-superuser` — promote to superuser

## Test User

You can promote any user to superuser with:

```http
PATCH /users/make-me-superuser
```

## Run Tests

```bash
pytest app/tests
```

