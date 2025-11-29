from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    role: str = Field(..., examples=["tenant", "landlord", "agent"])
    name: str
    email: EmailStr | None = None
    phone: str | None = None


class UserCreate(UserBase):
    # пока используется старым /users, позже заменим
    pass


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    telegram_id: str | None = None

    class Config:
        from_attributes = True


# 👇 новые схемы для auth

class UserRegister(BaseModel):
    role: str = Field(..., examples=["tenant", "landlord", "agent"])
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    password: str


class UserLogin(BaseModel):
    email: EmailStr | None = None
    phone: str | None = None
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TelegramAuth(BaseModel):
    telegram_id: str
    phone: str | None = None
    name: str | None = None
    role: str | None = "tenant"  # по умолчанию
