from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
)

from . import Base


class FeedAction(Base):
    __tablename__ = "feed_actions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, index=True, nullable=False)
    listing_id = Column(Integer, index=True, nullable=False)

    action = Column(String(16), nullable=False)  # like / dislike / favorite
    source = Column(String(16), nullable=True)   # web / telegram / other

    created_at = Column(DateTime(timezone=True), server_default=func.now())
