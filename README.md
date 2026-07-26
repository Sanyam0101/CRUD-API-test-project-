## Assignment 1:
# CRUD API Test Project

This project is a simple FastAPI-based CRUD API for managing tasks.

## What we built
- A FastAPI application in `main.py`
- SQLite persistence with a local `tasks.db` file
- Endpoints for listing, creating, updating, and deleting tasks
- Health check endpoint for basic verification

## Endpoints
- `GET /` → API info
- `GET /health` → health status
- `GET /tasks` → list all tasks
- `GET /tasks/{task_id}` → get a single task
- `POST /tasks` → create a task
- `PUT /tasks/{task_id}` → update a task
- `DELETE /tasks/{task_id}` → delete a task

## Run locally
1. Activate the virtual environment.
2. Start the server:

```bash
uvicorn main:app --reload
```

3. Open the docs page in your browser:

```text
http://127.0.0.1:8000/docs
```

## Basic test commands
You can test the API with curl:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/tasks
curl -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"New task\"}"
```

## Notes
- The app uses an in-memory list, so data resets when the server restarts.
- This repository is intended as a simple backend practice project.


## Assignment 2:
# CRUD API with SQLite

This project is a FastAPI-based task API that stores tasks in a SQLite database file called `tasks.db`.

## What this project does
- List all tasks
- Get one task by ID
- Create a new task
- Update an existing task
- Delete a task

## Why SQLite was chosen
SQLite was chosen because it uses a single file, needs no separate server, and keeps data after the server restarts.

## Database file
The database file is created automatically as `tasks.db` in the project folder.

## Run the app
Activate the virtual environment and start the server:

```bash
uvicorn main:app --reload


