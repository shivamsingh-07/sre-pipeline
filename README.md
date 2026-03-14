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
- **Docker** (optional; for building and running the containerized app)

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

## Docker

### Build the image

From the project root:

```bash
docker build -t sre-pipeline .
```

Use a specific tag if you prefer:

```bash
docker build -t sre-pipeline:1.0 .
```

### Run the container

The app listens on port 5000 inside the container. Map it to the host and pass the database URL:

```bash
docker run -d \
  --name sre-pipeline \
  -p 5000:5000 \
  -e DATABASE_URI="mysql+pymysql://USER:PASSWORD@host.docker.internal:3306/DBNAME" \
  sre-pipeline
```

- **`-p 5000:5000`** — maps container port 5000 to host 5000. Use `-p 8080:5000` to expose the app on host port 8080.
- **`-e DATABASE_URI=...`** — required. Use `host.docker.internal` (Docker Desktop on Mac/Windows) or your host’s IP so the container can reach MySQL on the host. On Linux you may need `--add-host=host.docker.internal:host-gateway` or the host network IP.

Optional environment variables:

```bash
docker run -d \
  --name sre-pipeline \
  -p 5000:5000 \
  -e DATABASE_URI="mysql+pymysql://user:pass@host.docker.internal:3306/school" \
  -e PORT=5000 \
  -e LOG_LEVEL=INFO \
  sre-pipeline
```

**Using a `.env` file** (Docker does not load `.env` by default; pass vars explicitly or use `--env-file`):

```bash
# Create a file (e.g. docker.env) with:
# DATABASE_URI=mysql+pymysql://...
# LOG_LEVEL=INFO

docker run -d --name sre-pipeline -p 5000:5000 --env-file docker.env sre-pipeline
```

**Apply migrations** before or after starting the container (run a one-off command in the same image):

```bash
docker run --rm --env-file docker.env sre-pipeline flask db upgrade
```

Then open **http://localhost:5000/** for the web UI and **http://localhost:5000/api/v1/healthcheck** to verify the API.

**Stop and remove the container:**

```bash
docker stop sre-pipeline
docker rm sre-pipeline
```

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
