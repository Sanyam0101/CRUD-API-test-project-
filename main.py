import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Task API", version="1.0")
DB_PATH = Path(__file__).resolve().parent / "tasks.db"


class TaskCreate(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )

        row_count = connection.execute("SELECT COUNT(*) AS count FROM tasks").fetchone()["count"]
        if row_count == 0:
            connection.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Buy groceries", 0),
                    ("Write report", 1),
                    ("Book dentist", 0),
                ],
            )

        connection.commit()


init_db()


@app.get("/")
async def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"],
    }


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/tasks")
async def list_tasks():
    with get_connection() as connection:
        rows = connection.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()

    return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]

@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    if task.title is None or not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required",
        )

    title = task.title.strip()
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, 0),
        )
        connection.commit()
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request body",
        )

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )

        if task.title is not None:
            connection.execute(
                "UPDATE tasks SET title = ? WHERE id = ?",
                (task.title.strip(), task_id),
            )

        if task.done is not None:
            connection.execute(
                "UPDATE tasks SET done = ? WHERE id = ?",
                (1 if task.done else 0, task_id),
            )

        connection.commit()
        updated = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return {"id": updated["id"], "title": updated["title"], "done": bool(updated["done"])}

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    with get_connection() as connection:
        existing = connection.execute(
            "SELECT id FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )

        connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        connection.commit()

    return None