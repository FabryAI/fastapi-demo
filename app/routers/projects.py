# In questo file vi lascio un esempio di come strutturerei la parte di commenti del codice nell'intero progetto.


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.security import get_current_user  # Dependency to get the authenticated user
from app.db.database import get_db  # Dependency to get a DB session
from app.models.project import Project as ProjectModel  # SQLAlchemy model for Project
from app.schemas.project import ProjectCreate, ProjectOut  # Pydantic schemas

import uuid

# Initialize the router for project-related endpoints
router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",  # Endpoint: POST /projects
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"},
    },
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Create a new project.
    Requires authentication.
    """
    new_project = ProjectModel(name=project.name)
    db.add(new_project)
    try:
        db.commit()
        db.refresh(new_project)  # Reload from DB to get generated fields (e.g. ID)
        return new_project
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Integrity error while creating project")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected database error while creating project")


@router.get(
    "",  # Endpoint: GET /projects
    response_model=list[ProjectOut],
    responses={
        400: {"description": "Invalid input"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)
def list_projects(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Retrieve all projects.
    Requires authentication.
    """
    try:
        projects = db.query(ProjectModel).all()
        return projects
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Unexpected database error while fetching projects"
        )


@router.get(
    "/{projectId}",  # Endpoint: GET /projects/{projectId}
    response_model=ProjectOut,
    responses={
        400: {"description": "Invalid input"},
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)
def get_project(
    projectId: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    """
    Retrieve a specific project by its UUID.
    Requires authentication.
    """
    try:
        project = db.query(ProjectModel).filter(ProjectModel.id == projectId).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Unexpected database error while fetching project"
        )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project
