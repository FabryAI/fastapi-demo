from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.task import Task as TaskModel
from app.models.project import Project
from app.models.user import User
from app.schemas.task import TaskInput, TaskOut
import uuid

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid input"},
        404: {"description": "Project or User not found"},
        500: {"description": "Internal server error"},
    },
)
def create_task(task: TaskInput, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    # Validazione progetto
    project = db.query(Project).filter(Project.id == task.project).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Validazione utente
    user = db.query(User).filter(User.id == task.user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Creazione Task
    new_task = TaskModel(
        project_id=task.project,
        user_id=task.user,
        activity=task.activity,
        start_time=task.datetimeStart,
        end_time=task.datetimeEnd,
    )

    db.add(new_task)
    try:
        db.commit()
        db.refresh(new_task)

        # Mapping manuale per restituire i campi come da schema OpenAPI
        return {
            "id": new_task.id,
            "project": new_task.project_id,
            "user": new_task.user_id,
            "activity": new_task.activity,
            "datetimeStart": new_task.start_time,
            "datetimeEnd": new_task.end_time,
        }

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error while creating task")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected database error while creating task")




@router.get(
    "",
    response_model=list[TaskOut],
    responses={
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"},
    },
)
def list_tasks(
    datetimeStart: Optional[datetime] = Query(None, description="Start of datetime filter range (ISO 8601)"),
    datetimeEnd: Optional[datetime] = Query(None, description="End of datetime filter range (ISO 8601)"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    try:
        query = db.query(TaskModel)
        if datetimeStart:
            query = query.filter(TaskModel.start_time >= datetimeStart)
        if datetimeEnd:
            query = query.filter(TaskModel.end_time <= datetimeEnd)

        tasks = query.all()

        return [
            TaskOut(
                id=task.id,
                project=task.project_id,
                user=task.user_id,
                activity=task.activity,
                datetimeStart=task.start_time,
                datetimeEnd=task.end_time,
            )
            for task in tasks
        ]

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Could not fetch tasks")


@router.get(
    "/{taskId}",
    response_model=TaskOut,
    responses={
        400: {"description": "Invalid input"},
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"},
    },
)
def get_task(taskId: uuid.UUID, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    task = db.query(TaskModel).filter(TaskModel.id == taskId).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskOut(
        id=task.id,
        project=task.project_id,
        user=task.user_id,
        activity=task.activity,
        datetimeStart=task.start_time,
        datetimeEnd=task.end_time,
    )



@router.put(
    "/{taskId}",
    response_model=TaskOut,
    responses={
        404: {"description": "Task not found"},
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"},
    },
)
def update_task(taskId: uuid.UUID, updated_task: TaskInput, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    task = db.query(TaskModel).filter(TaskModel.id == taskId).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.project_id = updated_task.project
    task.user_id = updated_task.user
    task.activity = updated_task.activity
    task.start_time = updated_task.datetimeStart
    task.end_time = updated_task.datetimeEnd

    try:
        db.commit()
        db.refresh(task)
        return TaskOut(
            id=task.id,
            project=task.project_id,
            user=task.user_id,
            activity=task.activity,
            datetimeStart=task.start_time,
            datetimeEnd=task.end_time,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error while updating task")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected database error while updating task")



@router.patch(
    "/{taskId}",
    response_model=TaskOut,
    responses={
        404: {"description": "Task not found"},
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"},
    },
)
def patch_task(taskId: uuid.UUID, updated_task: TaskInput, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    return update_task(taskId, updated_task, db)


@router.delete(
    "/{taskId}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Task not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_task(taskId: uuid.UUID, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    task = db.query(TaskModel).filter(TaskModel.id == taskId).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    try:
        db.delete(task)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error while deleting task")
