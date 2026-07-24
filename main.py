from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Task API", version="1.0")


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


TASKS = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Write report", "done": True},
    {"id": 3, "title": "Book dentist", "done": False},
]


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
    return TASKS


@app.get("/tasks/{task_id}")
async def get_task(task_id: int):
    for task in TASKS:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required",
        )

    new_id = max((t["id"] for t in TASKS), default=0) + 1
    new_task = {
        "id": new_id,
        "title": task.title.strip(),
        "done": False,
    }
    TASKS.append(new_task)
    return new_task


@app.put("/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    if task.title is None and task.done is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request body",
        )

    for existing_task in TASKS:
        if existing_task["id"] == task_id:
            if task.title is not None:
                existing_task["title"] = task.title.strip()

            if task.done is not None:
                existing_task["done"] = task.done

            return existing_task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    for index, task in enumerate(TASKS):
        if task["id"] == task_id:
            TASKS.pop(index)
            return None

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found",
    )