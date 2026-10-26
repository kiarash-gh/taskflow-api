import logging
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi import Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Task
from app.schemas import TaskCreate, TaskResponse, TaskUpdate
from app.logging_config import configure_logging


configure_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title="TaskFlow API")

@app.exception_handler(Exception)
async def handle_unexpected_exception(request, exc: Exception):
    logger.exception(
        "Unhandled exception: method=%s path=%s",
        request.method,
        request.url.path,
        exc_info=exc,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."},
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
):
    task = Task(
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
    )

    try:
        db.add(task)
        db.commit()
        db.refresh(task)
        logger.info("Task created successfully: task_id=%s", task.id)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while creating a task")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create task.",
        )

    return task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    completed: bool | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    statement = select(Task)

    if completed is not None:
        statement = statement.where(Task.completed == completed)

    statement = (
        statement
        .order_by(Task.id)
        .limit(limit)
        .offset(offset)
    )

    return db.scalars(statement).all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    updates = task_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(task, field, value)

    try:
        db.commit()
        db.refresh(task)
        logger.info("Task updated successfully: task_id=%s", task.id)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while updating a task")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update task.",
        )

    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    try:
        db.delete(task)
        db.commit()
        logger.info("Task deleted successfully: task_id=%s", task.id)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while deleting a task")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete task.",
        )


