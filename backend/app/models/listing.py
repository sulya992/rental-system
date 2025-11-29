from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, func

from . import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    city = Column(String(128), nullable=False)
    deal_type = Column(String(16), nullable=False, default="rent")
    property_type = Column(String(32), nullable=False, default="flat")
    price = Column(Numeric(12, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
