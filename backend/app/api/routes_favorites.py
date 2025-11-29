from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..deps import get_db
from ..models.favorite import Favorite
from ..models.listing import Listing
from ..schemas import FavoriteCreate, FavoriteRead, ListingRead

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("/", response_model=list[ListingRead])
def list_favorites(
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Возвращаем список объявлений, добавленных в избранное пользователем.
    """
    query = (
        db.query(Listing)
        .join(Favorite, Favorite.listing_id == Listing.id)
        .filter(Favorite.user_id == user_id)
        .filter(Listing.is_active.is_(True))
        .order_by(Favorite.created_at.desc())
    )
    return query.all()


@router.post("/", response_model=FavoriteRead)
def add_favorite(
    fav_in: FavoriteCreate,
    db: Session = Depends(get_db),
):
    """
    Добавить объявление в избранное (если ещё не в избранном).
    """
    fav = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == fav_in.user_id,
            Favorite.listing_id == fav_in.listing_id,
        )
        .first()
    )

    if fav is None:
        fav = Favorite(
            user_id=fav_in.user_id,
            listing_id=fav_in.listing_id,
        )
        db.add(fav)
        db.commit()
        db.refresh(fav)

    return fav


@router.delete("/{listing_id}")
def remove_favorite(
    listing_id: int,
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Удалить объявление из избранного для пользователя.
    """
    fav = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == user_id,
            Favorite.listing_id == listing_id,
        )
        .first()
    )
    if fav:
        db.delete(fav)
        db.commit()
    return {"status": "ok"}
