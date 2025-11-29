from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..deps import get_db
from ..models.listing import Listing
from ..models.preferences import TenantPreference
from ..models.feed_action import FeedAction
from ..schemas import ListingRead, FeedActionCreate
from ..models.lead import Lead
from ..models.favorite import Favorite

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/next", response_model=Optional[ListingRead])
def get_next_listing(
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    # 1. Получаем предпочтения пользователя (если есть)
    pref: TenantPreference | None = (
        db.query(TenantPreference)
        .filter(TenantPreference.user_id == user_id)
        .first()
    )

    # 2. Находим объявления, которые уже были в ленте/лайкнуты/дизлайкнуты
    seen_subq = (
        db.query(FeedAction.listing_id)
        .filter(FeedAction.user_id == user_id)
        .subquery()
    )

    # 3. Базовый запрос по активным объявлениям
    query = db.query(Listing).filter(Listing.is_active.is_(True))

    # 4. Применяем фильтры по предпочтениям
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

    # 6. Сортируем (сначала свежие)
    query = query.order_by(Listing.created_at.desc())

    listing = query.first()

    # Если ничего не нашли по предпочтениям, можно вернуть вообще любое первое активное,
    # которое юзер ещё не видел (fallback)
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
):
    action = FeedAction(
        user_id=action_in.user_id,
        listing_id=action_in.listing_id,
        action=action_in.action,
        source=action_in.source,
    )
    db.add(action)

    # Дополнительно: лайк -> лид, favorite -> избранное
    if action_in.action == "favorite":
        existing = (
            db.query(Favorite)
            .filter(
                Favorite.user_id == action_in.user_id,
                Favorite.listing_id == action_in.listing_id,
            )
            .first()
        )
        if existing is None:
            fav = Favorite(
                user_id=action_in.user_id,
                listing_id=action_in.listing_id,
            )
            db.add(fav)

    if action_in.action == "like":
        existing_lead = (
            db.query(Lead)
            .filter(
                Lead.tenant_id == action_in.user_id,
                Lead.listing_id == action_in.listing_id,
            )
            .first()
        )
        if existing_lead is None:
            # owner_id сейчас не знаем – позже будем брать из Listing.owner_id
            listing = db.query(Listing).filter(Listing.id == action_in.listing_id).first()
            owner_id = listing.owner_id if listing else None

            lead = Lead(
                tenant_id=action_in.user_id,
                listing_id=action_in.listing_id,
                owner_id=owner_id,
                status="new",
            )
            db.add(lead)

    db.commit()
    return {"status": "ok"}

