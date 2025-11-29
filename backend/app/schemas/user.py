from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    role: str = Field(..., examples=["tenant", "landlord", "agent"])
    name: str
    email: EmailStr | None = None
    phone: str | None = None


class UserCreate(UserBase):
    pass  # потом добавим пароль, если нужно


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
