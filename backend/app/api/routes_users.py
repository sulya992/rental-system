from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.user import User

from .. import models
from ..deps import get_db
from ..schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = models.user.User(  # или from ..models.user import User
        role=user_in.role,
        name=user_in.name,
        email=user_in.email,
        phone=user_in.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.user.User).all()
