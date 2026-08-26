# Project Plan & AI Agent Context

> **Note for AI Agents**: This file serves as the canonical context log for this repository. Review this file before starting new work and update it concisely upon completing milestones.

---

## 1. Project Overview
- **Name**: Task Management CRUD API
- **Purpose**: Lightweight backend API for task management built with FastAPI, PostgreSQL, and Docker.
- **Current Status**: Fully functional, PostgreSQL containerized, unit-tested (3/3 passing).

---

## 2. Environment & Tech Stack
- **Language & Runtime**: Python 3.13.0
- **Framework**: FastAPI `0.115.0`, Uvicorn `0.30.6`
- **Database**: PostgreSQL (`postgres:16-alpine`), `psycopg[binary]` v3 driver
- **Secrets Management**: `python-dotenv` reading `.env` (`DATABASE_URL`)
- **Containerization**: Docker & Docker Compose (`api` + `db` services, `taskdata` volume)
- **Testing**: pytest `8.3.3`, httpx `0.27.2`
- **Virtual Environment**: `.venv/` (Run tests with `.\.venv\Scripts\pytest.exe`)

---

## 3. Core Architecture & Files
- [main.py](file:///c:/Users/gargs/Desktop/backend%20practice/main.py): Primary FastAPI app entrypoint with dual database engine support (PostgreSQL via `psycopg` with SQLite fallback for offline pytest).
- [Dockerfile](file:///c:/Users/gargs/Desktop/backend%20practice/Dockerfile): Container build spec using `python:3.13-slim`.
- [.dockerignore](file:///c:/Users/gargs/Desktop/backend%20practice/.dockerignore): Ignores `.venv`, `__pycache__`, `.env`, `tasks.db`, etc.
- [docker-compose.yml](file:///c:/Users/gargs/Desktop/backend%20practice/docker-compose.yml): Multi-container orchestration (`api` app on port 8000 + `db` PostgreSQL on port 5432 with volume `taskdata`).
- [.env](file:///c:/Users/gargs/Desktop/backend%20practice/.env): Local secret config (`DATABASE_URL=postgresql://postgres:dev@localhost:5432/tasks`, git-ignored).
- [.env.example](file:///c:/Users/gargs/Desktop/backend%20practice/.env.example): Committed secret template file.
- [test_main.py](file:///c:/Users/gargs/Desktop/backend%20practice/test_main.py): Integration test suite using `TestClient`.
- [requirements.txt](file:///c:/Users/gargs/Desktop/backend%20practice/requirements.txt): Python dependencies including `psycopg[binary]` & `python-dotenv`.
- [README.md](file:///c:/Users/gargs/Desktop/backend%20practice/README.md): Project overview, A3 documentation, curl examples, and Docker Compose guide.

---

## 4. Implemented API Endpoints
| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/` | API Metadata | 200 OK |
| `GET` | `/health` | Health Check | 200 OK |
| `GET` | `/tasks` | List all tasks | 200 OK |
| `GET` | `/tasks/{task_id}` | Get task by ID | 200 OK / 404 |
| `POST` | `/tasks` | Create new task | 201 Created / 400 |
| `PUT` | `/tasks/{task_id}` | Update task title / completion status | 200 OK / 400 / 404 |
| `DELETE` | `/tasks/{task_id}` | Delete task by ID | 204 No Content / 404 |

---

## 5. Work Completed Log
1. **Initial Setup (A1)**: Created FastAPI boilerplate with in-memory storage.
2. **SQLite Database Integration (A2)**: Migrated storage from in-memory list to local `tasks.db` SQLite database with auto-schema setup & default seed data.
3. **Endpoint Validation & Test Suite**: Added Pydantic request validation, standard HTTP error codes (`400`, `404`), and pytest tests (`.\.venv\Scripts\pytest.exe`).
4. **Context Memory**: Created `project_plan.md` to persist AI agent working state.
5. **PostgreSQL & Docker Compose Stack (A3)**:
   - Configured `.env` & `.env.example` for secret management.
   - Installed `psycopg[binary]` (v3) & `python-dotenv`.
   - Updated `main.py` to use PostgreSQL parameterized queries with `psycopg3` (and automated SQLite fallback for offline pytest execution).
   - Created `docker-compose.yml` with `api` and `db` services plus persistent named volume `taskdata`.
   - Updated `README.md` with complete A3 instructions.

---

## 6. Guidelines for AI Agents Updating This File
- Keep sections structured and concise using Markdown tables or lists.
- Log new endpoints, architectural changes, or dependency additions under Section 3 & 4.
- Append completed tasks to Section 5.
- Always run `.\.venv\Scripts\pytest.exe` to verify zero regression before closing a task.
