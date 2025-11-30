from datetime import datetime
from pydantic import BaseModel


class LeadBase(BaseModel):
    tenant_id: int | None = None  # возьмём из current_user.id
    listing_id: int
    owner_id: int | None = None
    status: str = "new"


class LeadCreate(LeadBase):
    pass


class LeadRead(LeadBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
