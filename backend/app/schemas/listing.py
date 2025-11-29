from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class ListingBase(BaseModel):
    title: str
    city: str
    deal_type: str = "rent"       # rent / sale
    property_type: str = "flat"   # flat / house / room / commercial
    price: Decimal
    is_active: bool = True
    owner_id: int | None = None


class ListingCreate(ListingBase):
    pass


class ListingRead(ListingBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
