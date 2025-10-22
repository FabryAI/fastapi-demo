from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from utils import hash_password
import uuid

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid input"},
        409: {"description": "Conflict: email already registered"},
        500: {"description": "Internal server error"},
    },
)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user),):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_pw = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unexpected database error while creating user")



@router.get(
    "/{user_id}",
    response_model=UserOut,
    responses={
        200: {"description": "User found"},
        400: {"description": "Invalid input"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db), current_user: str = Depends(get_current_user),):
    try:
        user = db.query(User).filter(User.id == user_id).first()
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500, detail="Unexpected database error while fetching user"
        )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
