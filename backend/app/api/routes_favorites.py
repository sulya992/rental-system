from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..models.favorite import Favorite
from ..models.listing import Listing
from ..models.user import User
from ..schemas import FavoriteCreate, FavoriteRead, ListingRead

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("/", response_model=list[ListingRead])
def list_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Список объявлений, добавленных в избранное текущим пользователем.
    """
    query = (
        db.query(Listing)
        .join(Favorite, Favorite.listing_id == Listing.id)
        .filter(Favorite.user_id == current_user.id)
        .filter(Listing.is_active.is_(True))
        .order_by(Favorite.created_at.desc())
    )
    return query.all()


@router.post("/", response_model=FavoriteRead)
def add_favorite(
    fav_in: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Добавить объявление в избранное текущего пользователя.
    """
    existing = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == current_user.id,
            Favorite.listing_id == fav_in.listing_id,
        )
        .first()
    )

    if existing:
        return existing

    fav = Favorite(
        user_id=current_user.id,
        listing_id=fav_in.listing_id,
    )
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return fav


@router.delete("/{listing_id}")
def remove_favorite(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить объявление из избранного текущего пользователя.
    """
    fav = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == current_user.id,
            Favorite.listing_id == listing_id,
        )
        .first()
    )
    if fav:
        db.delete(fav)
        db.commit()
    return {"status": "ok"}
