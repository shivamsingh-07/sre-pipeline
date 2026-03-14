# SRE Pipeline — School Management System

A Flask-based **School Management System** exposing a versioned REST API and a simple web UI for managing students. Built for local development and as a reference for API design, migrations, testing, and runbooks.

## Purpose

- **REST API (v1):** CRUD for students, healthcheck, structured logging, and unit tests.
- **Web UI:** Browser interface that uses the API to list, add, edit, and delete students.
- **SRE-friendly:** Makefile for build/run/test, DB migrations (Flask-Migrate), healthcheck endpoint, and config via environment variables.

## Features

- **API versioning:** All API routes under `/api/v1/` (e.g. `/api/v1/students`, `/api/v1/healthcheck`).
- **Database:** SQLAlchemy with MySQL (PyMySQL driver); configurable via `DATABASE_URI`.
- **Migrations:** Flask-Migrate (Alembic) for schema changes; run with `flask db upgrade`.
- **Tests:** Pytest with in-memory SQLite; no MySQL required for unit tests.
- **Logging:** Configurable log level via `LOG_LEVEL`; API requests and errors logged with appropriate levels.

## Prerequisites

- **Python 3.10+**
- **MySQL** (for running the app against a real database; not needed for tests)
- **Make** (optional; you can run equivalent commands manually)

## Local setup

### 1. Clone and enter the repo

```bash
git clone <repo-url>
cd sre-pipeline
```

### 2. Environment variables

Create a `.env` file in the project root:

```bash
# Required for app + migrations (use SQLite for quick local try)
DATABASE_URI=mysql+pymysql://USER:PASSWORD@localhost/DBNAME

# Optional
LOG_LEVEL=INFO
```

For a **quick local run without MySQL**, you can point the app at SQLite by setting in `.env`:

```bash
DATABASE_URI=sqlite:///local.db
```

(You may need to run migrations once; see below.)

### 3. Build and run

Using the Makefile (recommended):

```bash
make build    # creates .venv, installs deps, runs migrations if DB is available
make run      # starts the API (Flask debug server)
```

Or without Make:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export FLASK_APP=run:app
flask db upgrade            # apply migrations (creates tables)
flask run --debug           # or: python run.py
```

### 4. Migrations (first time or after schema changes)

If you use MySQL or SQLite and have run `flask db upgrade` at least once, the `student` table is created. To generate new migrations after changing models:

```bash
flask db migrate -m "description"
flask db upgrade
```

## Running tests

```bash
make test
```

Or, with the venv activated:

```bash
pytest tests/ -v
```

Tests use an in-memory SQLite database; no MySQL or `.env` is required.

## API overview

| Method      | Endpoint                | Description                                       |
| ----------- | ----------------------- | ------------------------------------------------- |
| GET         | `/api/v1/healthcheck`   | Health check; returns `{"status": "ok"}`.         |
| GET         | `/api/v1/students`      | List all students.                                |
| POST        | `/api/v1/students`      | Create a student (JSON: `name`, `age`, `gender`). |
| GET         | `/api/v1/students/<id>` | Get one student.                                  |
| PUT / PATCH | `/api/v1/students/<id>` | Update a student (JSON body).                     |
| DELETE      | `/api/v1/students/<id>` | Delete a student.                                 |

**Example**

```bash
curl -X POST http://localhost:5000/api/v1/students \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "age": 20, "gender": "Female"}'
```

## Web UI

Open **http://localhost:5000/** in a browser to use the web interface. It talks to the same API to list, add, edit, and delete students.

## Makefile targets

| Target            | Description                                                                  |
| ----------------- | ---------------------------------------------------------------------------- |
| `make build`      | Create `.venv`, install dependencies, run `flask db upgrade` (if DB is set). |
| `make install`    | Install dependencies only (assumes venv exists).                             |
| `make migrate`    | Run `flask db upgrade`.                                                      |
| `make run`        | Start the app with `flask run --debug`.                                      |
| `make run-python` | Start the app with `python run.py`.                                          |
| `make test`       | Run `pytest tests/ -v`.                                                      |
| `make clean`      | Remove `.venv`, `__pycache__`, `.pytest_cache`, and `migrations/`.           |

## Project structure

```
sre-pipeline/
├── app/
│   ├── __init__.py       # create_app() factory
│   ├── config.py         # config from env
│   ├── extensions.py     # db, migrate
│   ├── web.py            # web UI routes (calls API via HTTP)
│   ├── api/v1/           # REST API v1
│   │   ├── __init__.py
│   │   └── routes.py     # students + healthcheck
│   ├── models/
│   │   ├── __init__.py
│   │   └── student.py
│   ├── templates/        # Jinja2 for web UI
│   └── static/           # CSS, etc.
├── migrations/           # Flask-Migrate (Alembic) scripts
├── tests/
│   ├── conftest.py       # pytest fixtures (app, client)
│   └── test_api_v1.py    # API unit tests
├── .env                  # local env (not committed)
├── conftest.py           # root pytest conftest
├── run.py                # entry point
├── requirements.txt
├── Makefile
└── README.md
```
