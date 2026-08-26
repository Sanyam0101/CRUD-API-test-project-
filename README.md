# Task Management CRUD API — Containerized Stack (Assignment A3)

A FastAPI-based task management API backed by a containerized **PostgreSQL** database, orchestrated using **Docker Compose**.

## Features
- **FastAPI** web framework with Pydantic schema validation.
- **PostgreSQL** containerized database with volume persistence (`taskdata`).
- **Secrets Management**: Configured via `.env` environment variables (git-ignored) with `.env.example` committed.
- **Single Command Startup**: Start both the API and database with one `docker compose up` command.

---

## Storage Evolution
- **A1**: In-memory list (data lost on server restart).
- **A2**: Local SQLite file (`tasks.db`).
- **A3 (Current)**: Containerized PostgreSQL database (`postgres:16-alpine`).

---

## Quick Start (One Command)

1. Clone repository and copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Ensure Docker Desktop is running, then start the entire stack:
   ```bash
   docker compose up -d
   ```

3. Open API docs in browser:
   ```text
   http://localhost:8000/docs
   ```

4. Stop the stack:
   ```bash
   docker compose down
   ```

---

## API Endpoints

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/` | API Information | 200 OK |
| `GET` | `/health` | Health Check | 200 OK |
| `GET` | `/tasks` | List all tasks | 200 OK |
| `GET` | `/tasks/{id}` | Get task by ID | 200 OK / 404 |
| `POST` | `/tasks` | Create a new task | 201 Created / 400 |
| `PUT` | `/tasks/{id}` | Update title or completion status | 200 OK / 400 / 404 |
| `DELETE` | `/tasks/{id}` | Delete task by ID | 204 No Content / 404 |

---

## Example cURL Commands

- **Check API health**:
  ```bash
  curl -i http://localhost:8000/health
  ```
- **List tasks**:
  ```bash
  curl -i http://localhost:8000/tasks
  ```
- **Create task**:
  ```bash
  curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Learn Docker & Postgres\"}"
  ```
- **Update task**:
  ```bash
  curl -i -X PUT http://localhost:8000/tasks/1 -H "Content-Type: application/json" -d "{\"done\":true}"
  ```
- **Delete task**:
  ```bash
  curl -i -X DELETE http://localhost:8000/tasks/1
  ```

---

## Inspecting Database inside Container

You can open `psql` inside the running PostgreSQL container to inspect rows directly:

```bash
docker exec -it taskdb psql -U postgres -d tasks
```
Inside `psql`:
- List tables: `\dt`
- View tasks: `SELECT * FROM tasks;`
- Exit prompt: `\q`
