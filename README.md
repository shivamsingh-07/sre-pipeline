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

The following must be installed before using this project. Requirements depend on how you run the app (local vs Docker).

### For local development (Makefile / Python)

| Tool       | Required | Notes                                                                                                                                                                                                         |
| ---------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Python** | Yes      | 3.10 or newer. Check with `python3 --version`.                                                                                                                                                                |
| **Make**   | Yes      | Used to run `make build`, `make run`, `make test`, etc. Check with `make --version`. On Windows you can use WSL, Git Bash, or install [Make for Windows](https://gnuwin32.sourceforge.net/packages/make.htm). |
| **MySQL**  | Optional | Required only if the app uses a MySQL `DATABASE_URI`. Not needed for running tests (tests use in-memory SQLite).                                                                                              |

### For Docker (docker-compose / docker build)

| Tool               | Required | Notes                                                                                        |
| ------------------ | -------- | -------------------------------------------------------------------------------------------- |
| **Docker**         | Yes      | Engine and CLI. Check with `docker --version`.                                               |
| **Docker Compose** | Yes      | v2 or later (e.g. `docker compose`). Check with `docker compose version`.                    |
| **Make**           | Optional | Convenient for wrapping `docker compose`; not required if you run `docker compose` directly. |

### For Vagrant (VM + Docker inside)

| Tool            | Required | Notes                                                                |
| --------------- | -------- | -------------------------------------------------------------------- |
| **Vagrant**     | Yes      | With VirtualBox or another provider. Check with `vagrant --version`. |
| **Vagrant box** | Yes      | `bento/ubuntu-24.04` (downloaded on first `vagrant up`).             |

### For running tests only

- **Python 3.10+** and **Make** (or run `pytest tests/ -v` manually after installing dependencies). No MySQL or Docker required.

## Make targets and order of execution

Use these targets in the order below depending on what you want to do.

### First-time local setup and run

1. **`make build`** — Create `.venv` and install dependencies. Run this first.
2. **`make migrate`** — (Optional) Apply migrations. Requires `DATABASE_URI` in `.env`. Run after build when using a DB.
3. **`make run`** — Start the Flask app. Use after build (and migrate if needed).

```bash
make build
make migrate   # if DB is set and you need to apply migrations
make run
```

### Running tests

1. **`make build`** — Ensures the venv and dependencies exist.
2. **`make test`** — Run the test suite. Does not require MySQL or `.env`.

```bash
make build
make test
```

### After changing dependencies

1. **`make install`** — Reinstall from `requirements.txt` (assumes `.venv` already exists from a previous `make build`).

### After changing the database schema (models)

1. **`make migrate`** — Apply pending migrations. Generate new ones locally with `flask db migrate -m "message"` then run `make migrate`.

### Clean slate (remove venv and caches)

1. **`make clean`** — Remove `.venv`, `__pycache__`, `.pytest_cache`, and the local `migrations/` directory. Use before a fresh `make build` if you want to start over.

```bash
make clean
make build
make run
```

### Docker (compose.yaml)

Use these targets when running the stack via Docker Compose. Requires **Docker** and **Docker Compose** (see Prerequisites). The stack uses **`compose.yaml`**: 2 API containers (app-1, app-2), 1 MySQL DB, 1 Nginx load balancer. Only Nginx is exposed (port **8080**); app ports stay private.

1. **`make docker-build`** — Build app images (and pull DB/Nginx images if needed). Run first or after changing the app or `Dockerfile`.
2. **`make docker-up`** — Start the stack in the background (`docker compose up -d` with `compose.yaml`).
3. **`make docker-logs`** — (Optional) Stream logs. Use `make docker-logs app-1` or leave default for all services.
4. **`make docker-down`** — Stop and remove the containers.

```bash
make docker-build
make docker-up
# API and Web UI at http://localhost:8080 (Nginx load-balances between 2 API containers)
make docker-logs   # optional
make docker-down   # when done
```

**Useful:** `make docker-ps` lists running containers. The Makefile uses `docker compose` (Compose v2), which picks up **`compose.yaml`** by default.

### Summary table (local)

| Order | Target         | When to use                                      |
| ----- | -------------- | ------------------------------------------------ |
| 1     | `make build`   | First time, or after clone / clean.              |
| 2     | `make migrate` | When you have a DB and need to apply migrations. |
| 3     | `make run`     | Start the app (after build).                     |
| —     | `make test`    | Run tests (after build).                         |
| —     | `make install` | After changing `requirements.txt`.               |
| —     | `make clean`   | When you want to remove venv and caches.         |

### Summary table (Docker)

| Order | Target              | When to use                                     |
| ----- | ------------------- | ----------------------------------------------- |
| 1     | `make docker-build` | First time, or after changing app / Dockerfile. |
| 2     | `make docker-up`    | Start stack (2 API + DB + Nginx).               |
| —     | `make docker-logs`  | Stream logs.                                    |
| —     | `make docker-ps`    | List containers.                                |
| —     | `make docker-down`  | Stop and remove containers.                     |

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

# Optional: base URL for web UI to call the API (default: same host as request)
# Set in Docker/compose when web calls API via Nginx, e.g. BASE_URL=http://nginx
API_BASE_URL=

# Optional
LOG_LEVEL=INFO
```

For a **quick local run without MySQL**, you can point the app at SQLite by setting in `.env`:

```bash
DATABASE_URI=sqlite:///local.db
```

(You may need to run migrations once; see below.) The web UI uses **`API_BASE_URL`** (or **`BASE_URL`** in compose) to reach the API; if unset, it uses the current request host.

### 3. Build and run

Using the Makefile (recommended):

```bash
make build    # creates .venv, installs deps
make migrate  # optional: apply migrations if DATABASE_URI is set
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

Then open **http://localhost:5000/** for the web UI and **http://localhost:5000/api/v1/healthcheck** to verify the API. When using **compose.yaml** (2 API + Nginx), use **http://localhost:8080** instead (Nginx is the only public port).

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

Open **http://localhost:5000/** (single app) or **http://localhost:8080/** (compose stack with Nginx) in a browser. The web UI calls the API (via **API_BASE_URL** / **BASE_URL** when set, e.g. in containers) to list, add, edit, and delete students.

## Vagrant

The **Vagrantfile** spins up a VM (bento/ubuntu-24.04), provisions it (apt update/upgrade, Docker via https://get.docker.com, add vagrant to docker group), and runs **`docker compose -f /vagrant/compose.yaml up -d`** so the full stack (2 API + 1 DB + 1 Nginx) runs inside the VM. The project directory is synced to `/vagrant`.

**Prerequisites:** Vagrant, VirtualBox (or another provider).

```bash
vagrant up
# API and Web UI: http://localhost:8080 (if port 8080 is forwarded) or use the VM’s private_network IP (e.g. http://10.0.0.10:8080)
vagrant halt   # when done
```

The Vagrantfile uses a **private network** (e.g. `10.0.0.10`). To access the app from the host, either forward port 8080 in the Vagrantfile (`config.vm.network "forwarded_port", guest: 8080, host: 8080`) or use the VM IP and port 8080.

## Makefile targets

| Target              | Description                                                        |
| ------------------- | ------------------------------------------------------------------ |
| `make build`        | Create `.venv` and install dependencies.                           |
| `make install`      | Install dependencies only (assumes venv exists).                   |
| `make migrate`      | Run `flask db upgrade`.                                            |
| `make run`          | Start the app with `flask run --debug`.                            |
| `make run-python`   | Start the app with `python run.py`.                                |
| `make test`         | Run `pytest tests/ -v`.                                            |
| `make lint`         | Run ruff check and format check.                                   |
| `make ci`           | Run build, then lint, then test.                                   |
| `make clean`        | Remove `.venv`, `__pycache__`, `.pytest_cache`, and `migrations/`. |
| `make docker-build` | Build images with `docker compose` (uses `compose.yaml`).          |
| `make docker-up`    | Start stack (2 API + DB + Nginx) in background.                    |
| `make docker-down`  | Stop and remove containers.                                        |
| `make docker-logs`  | Stream compose logs.                                               |
| `make docker-ps`    | List running compose containers.                                   |

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
├── nginx/
│   └── nginx.conf        # load balancer for 2 API containers (committed)
├── migrations/           # Flask-Migrate (Alembic) scripts
├── tests/
│   ├── conftest.py       # pytest fixtures (app, client)
│   └── test_api_v1.py    # API unit tests
├── .env                  # local env (not committed)
├── conftest.py           # root pytest conftest
├── compose.yaml          # 2 API + 1 DB + 1 Nginx; only port 8080 exposed
├── docker-compose.yaml   # alternate Compose file (same stack)
├── run.py                # entry point
├── requirements.txt
├── Makefile
├── Vagrantfile           # VM provision (Docker, then docker compose up)
├── Dockerfile
└── README.md
```
