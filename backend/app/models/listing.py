from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Boolean,
    DateTime,
    func,
)

from . import Base


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)

    # Владелец объявления (пока без внешнего ключа, в будущем добавим FK на users)
    owner_id = Column(Integer, nullable=True, index=True)

    title = Column(String(255), nullable=False)
    city = Column(String(128), nullable=False)

    deal_type = Column(String(16), nullable=False, default="rent")      # rent / sale
    property_type = Column(String(32), nullable=False, default="flat")  # flat / house / room / commercial

    price = Column(Numeric(12, 2), nullable=False)

    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
