from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..models.listing import Listing
from ..models.preferences import TenantPreference
from ..models.feed_action import FeedAction
from ..models.favorite import Favorite
from ..models.lead import Lead
from ..models.user import User
from ..schemas import ListingRead, FeedActionCreate

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/next", response_model=Optional[ListingRead])
def get_next_listing(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Вернуть следующее подходящее объявление для текущего пользователя.
    """
    user_id = current_user.id

    # 1. Предпочтения пользователя
    pref: TenantPreference | None = (
        db.query(TenantPreference)
        .filter(TenantPreference.user_id == user_id)
        .first()
    )

    # 2. Объявления, которые уже были в ленте (лайк/дизлайк/фаворит)
    seen_subq = (
        db.query(FeedAction.listing_id)
        .filter(FeedAction.user_id == user_id)
        .subquery()
    )

    # 3. Базовый запрос по активным объявлениям
    query = db.query(Listing).filter(Listing.is_active.is_(True))

    # 4. Фильтры по предпочтениям
    if pref:
        if pref.city:
            query = query.filter(Listing.city == pref.city)
        if pref.deal_type:
            query = query.filter(Listing.deal_type == pref.deal_type)
        if pref.property_type:
            query = query.filter(Listing.property_type == pref.property_type)
        if pref.price_min is not None:
            query = query.filter(Listing.price >= pref.price_min)
        if pref.price_max is not None:
            query = query.filter(Listing.price <= pref.price_max)

    # 5. Исключаем уже просмотренные
    query = query.filter(~Listing.id.in_(select(seen_subq.c.listing_id)))

    # 6. Сортируем по свежести
    query = query.order_by(Listing.created_at.desc())

    listing = query.first()

    # fallback: если ничего не нашли по предпочтениям
    if listing is None:
        fallback_query = (
            db.query(Listing)
            .filter(Listing.is_active.is_(True))
            .filter(~Listing.id.in_(select(seen_subq.c.listing_id)))
            .order_by(Listing.created_at.desc())
        )
        listing = fallback_query.first()

    return listing


@router.post("/action")
def save_feed_action(
    action_in: FeedActionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Сохранить действие пользователя по объявлению: like / dislike / favorite.
    Параллельно:
    - favorite -> добавляем в избранное
    - like -> создаём лид (если его ещё нет)
    """
    user_id = current_user.id

    action = FeedAction(
        user_id=user_id,
        listing_id=action_in.listing_id,
        action=action_in.action,
        source=action_in.source,
    )
    db.add(action)

    # favorite -> избранное
    if action_in.action == "favorite":
        existing_fav = (
            db.query(Favorite)
            .filter(
                Favorite.user_id == user_id,
                Favorite.listing_id == action_in.listing_id,
            )
            .first()
        )
        if existing_fav is None:
            fav = Favorite(
                user_id=user_id,
                listing_id=action_in.listing_id,
            )
            db.add(fav)

    # like -> лид
    if action_in.action == "like":
        existing_lead = (
            db.query(Lead)
            .filter(
                Lead.tenant_id == user_id,
                Lead.listing_id == action_in.listing_id,
            )
            .first()
        )
        if existing_lead is None:
            listing = (
                db.query(Listing)
                .filter(Listing.id == action_in.listing_id)
                .first()
            )
            owner_id = listing.owner_id if listing else None

            lead = Lead(
                tenant_id=user_id,
                listing_id=action_in.listing_id,
                owner_id=owner_id,
                status="new",
            )
            db.add(lead)

    db.commit()
    return {"status": "ok"}
