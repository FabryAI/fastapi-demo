![FastAPI Cover](assets/images/fastapi_demo_cover.png)

# ⚡ FastAPI Demo — Modular Backend for Modern APIs

A **production-style FastAPI backend** demonstrating backend engineering skills with modern tooling: Docker, PostgreSQL, SQLAlchemy ORM, JWT authentication, and Pytest integration.

This project represents a **Time Tracker API** where users can manage projects, tasks, and reports — all through a clean, modular RESTful architecture.

---

## 🚀 Features

- ⚙️ **FastAPI** modular app structure (`routers`, `schemas`, `services`)
- 🧱 **SQLAlchemy + Alembic** migrations for PostgreSQL
- 🔐 **JWT Authentication** (login/register flow)
- 🧰 **Environment-based configuration** via `.env`
- 🧪 **Pytest** unit and integration testing
- 🐳 **Docker Compose** for full stack setup (App + DB + PgAdmin)
- 📜 **OpenAPI docs** auto-generated at `/docs`

---

## 🧭 Project Structure

```
fastapi-demo/
├── app/
│   ├── main.py              ← FastAPI entrypoint
│   ├── core/                ← config, dependencies, utils
│   ├── models/              ← SQLAlchemy models
│   ├── schemas/             ← Pydantic schemas
│   ├── services/            ← business logic / CRUD
│   └── routers/             ← API endpoints
│
├── alembic/                 ← DB migrations
├── assets/                  ← documentation images
├── tests/                   ← pytest suite
├── Dockerfile               ← app container
├── docker-compose.yml       ← app + PostgreSQL + PgAdmin
├── pyproject.toml           ← Poetry dependencies
├── .env.example             ← example environment config
└── README.md
```

---

## 🧠 Tech Stack

- **Python 3.11+**
- **FastAPI** – async web framework
- **SQLAlchemy + Alembic** – ORM & migrations
- **PostgreSQL** – relational database
- **Pytest** – testing framework
- **Docker & Docker Compose** – environment orchestration
- **Poetry** – dependency management
- **Pydantic** – validation & serialization
- **python-jose**, **passlib**, **bcrypt** – for JWT auth

---

## ⚙️ Setup Guide (Docker + Local)

### 🔹 Prerequisites
- **Docker** + **Docker Compose** installed  
- *(Optional)* **Python 3.11** + **Poetry** if you want to run locally

---

### 🚀 Quick Start with Docker

From the project root:

```bash
docker compose up --build -d
```

This command starts:
- **app** → FastAPI backend at [http://localhost:8000](http://localhost:8000)
  - Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- **db** → PostgreSQL
- **pgadmin** → Database web interface at [http://localhost:5050](http://localhost:5050)

> Tables are **automatically created** at startup (`Base.metadata.create_all`).
> A **seed script** (`app/db/init_db.py`) inserts a demo user and project.

---

### 🗄️ Configure Database via PgAdmin (optional)

If you don’t see the DB at first run, open **pgAdmin** at [http://localhost:5050](http://localhost:5050) and log in with:

**PgAdmin credentials:**
- Email: `admin@admin.com`
- Password: `admin`

**Add a new server:**
1. Click **Add New Server**
2. **General → Name:** `Postgres` (any name works)
3. **Connection:**
   - Host: `db`
   - Port: `5432`
   - Username: `postgres`
   - Password: `password`
4. Click **Save**

Then create the database (if missing):
- *Servers → Postgres → Databases → Create → Database*
  - **Database:** `fastapi_demo`  
  - Save ✅

![PgAdmin setup](assets/images/db_setting_up.png)

---

### 🔐 Environment Variables

Main environment settings (already defined in `docker-compose.yml`):

```dotenv
DATABASE_URL=postgresql://postgres:password@db:5432/fastapi_demo
SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> When running **outside Docker**, replace `@db` with `@localhost`.

---

### 🧪 Test the API (Swagger)

1. Open **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)  
2. **Login:** `POST /auth/login` using the demo user:
   - `username`: `admin@example.com`
   - `password`: `admin123`
3. Click **Authorize** in Swagger and enter the same credentials.  
   Swagger automatically applies the JWT token to secured endpoints.

![Swagger Auth](assets/images/auth_swagger.png)

#### Main Endpoints

| Group | Endpoint | Description |
|--------|-----------|--------------|
| **Auth** | `POST /auth/login` | Obtain JWT token |
| **Users** | `POST /users/`, `GET /users/{id}` | Manage users |
| **Projects** | `GET /projects/`, `POST /projects/` | Manage projects |
| **Tasks** | `GET /tasks/`, `POST /tasks/`, `PUT /tasks/{id}`, `DELETE /tasks/{id}` | Manage tasks |
| **Reports** | `GET /report?start_date=&end_date=` | Aggregate time by project |

---

## 🧩 Running Locally (without Docker)

```bash
poetry install
cp .env.example .env
poetry run uvicorn app.main:app --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing

Tests are written with **pytest** and located in `app/tests`.

Run them with:

```bash
poetry run pytest -v
```

**Test DB configuration:**
```dotenv
DATABASE_URL=postgresql://postgres:password@localhost:5432/testdb
```

---

## 🧰 Troubleshooting

| Problem | Cause / Fix |
|----------|--------------|
| `could not translate host name "db"` | Running outside Docker → use `localhost` instead |
| `python-multipart` missing | Required for form data auth → reinstall deps |
| `email-validator` missing | Rebuild Docker image (`docker compose up --build -d`) |
| `bcrypt` / `passlib` version errors | Locked to `bcrypt==3.2.2` for compatibility |

---

## 🛣️ Roadmap

- [ ] Role-based permissions (RBAC)
- [ ] Async SQLAlchemy support
- [ ] Redis caching layer
- [ ] Cloud deployment (Render / Railway)
- [ ] CI/CD pipeline integration

---

## 📄 License

This project is for educational and portfolio purposes.  
Released under the **MIT License**.

---

## ⚠️ Disclaimer  
This project was originally developed as part of a private backend assessment.  
The entire implementation — architecture, database models, and API endpoints — was built from scratch by me within a three-day timeframe.  
For privacy and confidentiality reasons, all company-specific references and challenge materials have been removed.  
It is now published solely as a public technical example for educational and portfolio purposes.

---

