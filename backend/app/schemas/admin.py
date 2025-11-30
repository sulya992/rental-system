from datetime import datetime
from pydantic import BaseModel, EmailStr


class AdminUserUpdate(BaseModel):
    role: str | None = None      # tenant / landlord / agent / admin
    is_active: bool | None = None


class AdminUserRead(BaseModel):
    id: int
    name: str
    role: str
    email: EmailStr | None = None
    phone: str | None = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AdminListingRead(BaseModel):
    id: int
    title: str
    city: str
    deal_type: str
    property_type: str
    price: float
    is_active: bool
    owner_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True
