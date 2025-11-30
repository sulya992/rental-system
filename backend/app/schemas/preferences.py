from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class TenantPreferenceBase(BaseModel):
    city: str | None = None
    deal_type: str | None = None        # rent / sale
    property_type: str | None = None    # flat / house / room / ...

    price_min: Decimal | None = None
    price_max: Decimal | None = None

    rooms_min: int | None = None
    rooms_max: int | None = None

    area_min: int | None = None
    area_max: int | None = None


class TenantPreferenceCreate(TenantPreferenceBase):
    user_id: int | None = None  # будет игнорироваться и подменяться текущим пользователем



class TenantPreferenceRead(TenantPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
