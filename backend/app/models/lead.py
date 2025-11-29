from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
)

from . import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(Integer, index=True, nullable=False)
    listing_id = Column(Integer, index=True, nullable=False)
    owner_id = Column(Integer, index=True, nullable=True)

    status = Column(String(32), nullable=False, server_default="new")
    # new / in_progress / closed - можем потом добавить отдельный enum

    created_at = Column(DateTime(timezone=True), server_default=func.now())
