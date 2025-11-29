from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    func,
    UniqueConstraint,
)

from . import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, index=True, nullable=False)
    listing_id = Column(Integer, index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "listing_id", name="uq_favorites_user_listing"),
    )
