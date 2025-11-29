from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class ListingBase(BaseModel):
    title: str
    city: str
    deal_type: str = "rent"       # rent / sale
    property_type: str = "flat"   # flat / house / room / ...
    price: Decimal
    is_active: bool = True


class ListingCreate(ListingBase):
    pass


class ListingRead(ListingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
