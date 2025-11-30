from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..models.listing import Listing
from ..models.user import User
from ..schemas import ListingCreate, ListingRead

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("/", response_model=ListingRead)
def create_listing(
    listing_in: ListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать объявление. Владелец = текущий пользователь.
    """
    listing = Listing(
        title=listing_in.title,
        city=listing_in.city,
        deal_type=listing_in.deal_type,
        property_type=listing_in.property_type,
        price=listing_in.price,
        is_active=listing_in.is_active,
        owner_id=current_user.id,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing

@router.get("/", response_model=list[ListingRead])
def list_listings(
    city: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Список активных объявлений (публичный).
    """
    query = db.query(Listing).filter(Listing.is_active.is_(True))
    if city:
        query = query.filter(Listing.city == city)
    listings = query.order_by(Listing.created_at.desc()).all()
    return listings

@router.get("/my", response_model=list[ListingRead])
def list_my_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Объявления текущего пользователя как владельца/агента.
    """
    listings = (
        db.query(Listing)
        .filter(Listing.owner_id == current_user.id)
        .order_by(Listing.created_at.desc())
        .all()
    )
    return listings


@router.get("/", response_model=list[ListingRead])
def list_listings(
    city: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """
    Список активных объявлений (публичный, без авторизации).
    """
    query = db.query(Listing).filter(Listing.is_active.is_(True))
    if city:
        query = query.filter(Listing.city == city)
    listings = query.order_by(Listing.created_at.desc()).all()
    return listings


@router.get("/{listing_id}", response_model=ListingRead)
def get_listing(
    listing_id: int,
    db: Session = Depends(get_db),
):
    """
    Детальная по одному объявлению.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing or not listing.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )
    return listing


@router.put("/{listing_id}", response_model=ListingRead)
def update_listing(
    listing_id: int,
    listing_in: ListingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить объявление (только владелец или админ).
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    if listing.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to edit this listing",
        )

    for field, value in listing_in.model_dump().items():
        setattr(listing, field, value)

    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.delete("/{listing_id}")
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Мягкое удаление: просто делаем is_active = false.
    Только владелец или админ.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found",
        )

    if listing.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this listing",
        )

    listing.is_active = False
    db.add(listing)
    db.commit()
    return {"status": "ok"}
