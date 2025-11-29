from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings
from .models import Base  # ВАЖНО: тянет за собой все модели


engine = create_engine(
    settings.database_url,
    future=True,
    echo=False,  # включишь True, если захочешь видеть SQL в логах
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def init_db() -> None:
    """Создаёт таблицы в БД, если их ещё нет."""
    Base.metadata.create_all(bind=engine)
