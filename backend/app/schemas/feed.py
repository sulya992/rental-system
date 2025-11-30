from datetime import datetime
from pydantic import BaseModel, Field


class FeedActionBase(BaseModel):
    user_id: int | None = None  # игнорируем, берём из текущего пользователя
    listing_id: int
    action: str = Field(..., examples=["like", "dislike", "favorite"])
    source: str | None = Field(default="web", examples=["web", "telegram"])


class FeedActionCreate(FeedActionBase):
    pass


class FeedActionRead(FeedActionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
