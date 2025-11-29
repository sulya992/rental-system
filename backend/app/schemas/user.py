from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    role: str = Field(..., examples=["tenant", "landlord", "agent"])
    name: str
    email: EmailStr | None = None
    phone: str | None = None


class UserCreate(UserBase):
    # позже сюда добавим пароль, если понадобится
    pass


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (раньше было orm_mode
