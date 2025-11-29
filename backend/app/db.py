from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings
from .models import Base  # 👈 добавили

engine = create_engine(
    settings.database_url,
    future=True,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def init_db():
    # Важно: перед вызовом импортировать все модели,
    # чтобы они были зарегистрированы в Base.metadata
    Base.metadata.create_all(bind=engine)
