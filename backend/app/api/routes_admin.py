from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..models.user import User
from ..models.listing import Listing
from ..schemas import AdminUserUpdate, AdminUserRead, AdminListingRead

router = APIRouter(prefix="/admin", tags=["admin"])


def ensure_admin(user: User):
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )


@router.get("/users", response_model=list[AdminUserRead])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Список пользователей (только для админа).
    """
    ensure_admin(current_user)

    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.patch("/users/{user_id}", response_model=AdminUserRead)
def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить роль/активность пользователя (только админ).
    """
    ensure_admin(current_user)

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/listings", response_model=list[AdminListingRead])
def admin_list_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    city: str | None = Query(default=None),
    owner_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
):
    """
    Полный список объявлений (включая неактивные), фильтруется по городу/владельцу/статусу.
    Только для админа.
    """
    ensure_admin(current_user)

    query = db.query(Listing)

    if city:
        query = query.filter(Listing.city == city)
    if owner_id is not None:
        query = query.filter(Listing.owner_id == owner_id)
    if is_active is not None:
        query = query.filter(Listing.is_active == is_active)

    listings = query.order_by(Listing.created_at.desc()).all()
    return listings
