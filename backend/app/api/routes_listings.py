from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..deps import get_db
from ..models.listing import Listing
from ..schemas import ListingCreate, ListingRead

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("/", response_model=ListingRead)
def create_listing(listing_in: ListingCreate, db: Session = Depends(get_db)):
    listing = Listing(
        title=listing_in.title,
        city=listing_in.city,
        deal_type=listing_in.deal_type,
        property_type=listing_in.property_type,
        price=listing_in.price,
        is_active=listing_in.is_active,
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("/", response_model=list[ListingRead])
def list_listings(
    city: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Listing).filter(Listing.is_active.is_(True))
    if city:
        query = query.filter(Listing.city == city)
    return query.order_by(Listing.created_at.desc()).all()
