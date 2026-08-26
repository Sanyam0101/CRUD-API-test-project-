import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:dev@localhost:5432/tasks")
SQLITE_DB_PATH = Path(__file__).resolve().parent / "tasks.db"

app = FastAPI(title="Task API", version="1.0")


class TaskCreate(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


def get_db_engine():
    if DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://"):
        try:
            import psycopg
            from psycopg.rows import dict_row

            conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
            return "postgres", conn
        except Exception:
            pass

    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return "sqlite", conn


@contextmanager
def get_connection():
    engine_type, conn = get_db_engine()
    try:
        yield engine_type, conn
    finally:
        conn.close()


def init_db():
    try:
        with get_connection() as (engine_type, conn):
            if engine_type == "postgres":
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS tasks (
                            id SERIAL PRIMARY KEY,
                            title TEXT NOT NULL,
                            done BOOLEAN NOT NULL DEFAULT FALSE
                        )
                        """
                    )
                    cur.execute("SELECT COUNT(*) AS count FROM tasks")
                    row = cur.fetchone()
                    count = row["count"] if isinstance(row, dict) else row[0]
                    if count == 0:
                        cur.executemany(
                            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                            [
                                ("Buy groceries", False),
                                ("Write report", True),
                                ("Book dentist", False),
                            ],
                        )
                    conn.commit()
            else:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        done INTEGER NOT NULL DEFAULT 0
                    )
                    """
                )
                row_count = conn.execute("SELECT COUNT(*) AS count FROM tasks").fetchone()["count"]
                if row_count == 0:
                    conn.executemany(
                        "INSERT INTO tasks (title, done) VALUES (?, ?)",
                        [
                            ("Buy groceries", 0),
                            ("Write report", 1),
                            ("Book dentist", 0),
                        ],
                    )
                conn.commit()
    except Exception as e:
        print(f"Database initialization note: {e}")


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
    with get_connection() as (engine_type, conn):
        if engine_type == "postgres":
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
                rows = cur.fetchall()
                return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]
        else:
            rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
            return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]


@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    with get_connection() as (engine_type, conn):
        if engine_type == "postgres":
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Task {task_id} not found",
                    )
                return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        else:
            row = conn.execute(
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
    with get_connection() as (engine_type, conn):
        if engine_type == "postgres":
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
                    (title, False),
                )
                row = cur.fetchone()
                conn.commit()
                return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        else:
            cursor = conn.execute(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                (title, 0),
            )
            conn.commit()
            row = conn.execute(
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

    with get_connection() as (engine_type, conn):
        if engine_type == "postgres":
            with conn.cursor() as cur:
                cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
                existing = cur.fetchone()
                if existing is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Task {task_id} not found",
                    )

                new_title = task.title.strip() if task.title is not None else existing["title"]
                new_done = task.done if task.done is not None else bool(existing["done"])

                cur.execute(
                    "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
                    (new_title, new_done, task_id),
                )
                updated = cur.fetchone()
                conn.commit()
                return {"id": updated["id"], "title": updated["title"], "done": bool(updated["done"])}
        else:
            existing = conn.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

            if existing is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {task_id} not found",
                )

            if task.title is not None:
                conn.execute(
                    "UPDATE tasks SET title = ? WHERE id = ?",
                    (task.title.strip(), task_id),
                )

            if task.done is not None:
                conn.execute(
                    "UPDATE tasks SET done = ? WHERE id = ?",
                    (1 if task.done else 0, task_id),
                )

            conn.commit()
            updated = conn.execute(
                "SELECT id, title, done FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
            return {"id": updated["id"], "title": updated["title"], "done": bool(updated["done"])}


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    with get_connection() as (engine_type, conn):
        if engine_type == "postgres":
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
                existing = cur.fetchone()
                if existing is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Task {task_id} not found",
                    )
                cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                conn.commit()
        else:
            existing = conn.execute(
                "SELECT id FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

            if existing is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {task_id} not found",
                )

            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()

    return None