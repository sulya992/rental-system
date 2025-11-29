from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    func,
)

from . import Base


class TenantPreference(Base):
    __tablename__ = "tenant_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)

    city = Column(String(128), nullable=True)
    deal_type = Column(String(16), nullable=True)       # rent / sale
    property_type = Column(String(32), nullable=True)   # flat / house / room / ...

    price_min = Column(Numeric(12, 2), nullable=True)
    price_max = Column(Numeric(12, 2), nullable=True)

    rooms_min = Column(Integer, nullable=True)
    rooms_max = Column(Integer, nullable=True)

    area_min = Column(Integer, nullable=True)
    area_max = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
