from datetime import datetime
from pydantic import BaseModel


class FavoriteBase(BaseModel):
    user_id: int | None = None  # будем подставлять current_user.id
    listing_id: int



class FavoriteCreate(FavoriteBase):
    pass


class FavoriteRead(FavoriteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
