#!/usr/bin/env bash
set -e

echo "Создаю директории..."

mkdir -p backend/app/api
mkdir -p backend/app/models
mkdir -p telegram-bot/bot
mkdir -p frontend
mkdir -p docs
mkdir -p infra/nginx

echo "Создаю backend файлы..."

cat > backend/app/__init__.py << 'EOF'
# Backend application package
EOF

cat > backend/app/config.py << 'EOF'
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "local"
    database_url: str

    model_config = SettingsConfigDict(
        env_prefix="",
        extra="ignore",
    )


settings = Settings()
EOF

cat > backend/app/db.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

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
EOF

cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI

from .config import settings
from .api.routes_users import router as users_router
from .api.routes_listings import router as listings_router
from .api.routes_feed import router as feed_router

app = FastAPI(
    title="Real Estate Tinder API",
    version="0.1.0",
)

app.include_router(users_router)
app.include_router(listings_router)
app.include_router(feed_router)


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment}
EOF

cat > backend/app/api/__init__.py << 'EOF'
# API routers package
EOF

cat > backend/app/api/routes_users.py << 'EOF'
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me():
    # Stub endpoint for now
    return {"detail": "user endpoint stub"}
EOF

cat > backend/app/api/routes_listings.py << 'EOF'
from fastapi import APIRouter

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/")
async def list_listings():
    # Stub endpoint for now
    return []
EOF

cat > backend/app/api/routes_feed.py << 'EOF'
from fastapi import APIRouter

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/next")
async def get_next_listing():
    # Stub endpoint for now
    return {"detail": "no listings yet"}
EOF

cat > backend/app/models/__init__.py << 'EOF'
from sqlalchemy.orm import declarative_base

Base = declarative_base()
EOF

cat > backend/app/models/user.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, func

from . import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(32), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone = Column(String(32), unique=True, index=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
EOF

cat > backend/app/models/listing.py << 'EOF'
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
EOF

cat > backend/requirements.txt << 'EOF'
fastapi
uvicorn[standard]
SQLAlchemy
psycopg2-binary
pydantic
pydantic-settings
python-dotenv
alembic
EOF

cat > backend/Dockerfile << 'EOF'
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

echo "Создаю telegram-bot файлы (заглушки)..."

cat > telegram-bot/bot/__init__.py << 'EOF'
# Telegram bot package
EOF

cat > telegram-bot/bot/main.py << 'EOF'
def main():
    # Telegram bot placeholder for future implementation
    print("Telegram bot placeholder. Implement me later.")


if __name__ == "__main__":
    main()
EOF

cat > telegram-bot/requirements.txt << 'EOF'
aiogram
python-dotenv
EOF

cat > telegram-bot/Dockerfile << 'EOF'
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot ./bot

CMD ["python", "bot/main.py"]
EOF

echo "Создаю frontend заглушку..."

cat > frontend/README.md << 'EOF'
# Frontend

Placeholder for the real estate tinder web frontend (React / Next.js planned).
EOF

echo "Создаю docs..."

cat > docs/requirements.md << 'EOF'
# Project Requirements (Draft)

- Roles: tenant, landlord, agent, admin
- Core features:
  - User registration / authentication
  - Listings CRUD (rent / sale)
  - Preferences-based feed ("tinder-style" recommendations)
  - Future: Telegram bot integration
EOF

cat > docs/architecture.md << 'EOF'
# Architecture (Draft)

- Monorepo structure:
  - backend: FastAPI + PostgreSQL
  - telegram-bot: separate service using the same API / DB
  - frontend: web client consuming backend API
- Infrastructure:
  - Docker + docker-compose for local and server deployments
  - GCP VM as initial hosting target
EOF

echo "Создаю infra/nginx..."

cat > infra/nginx/nginx.conf << 'EOF'
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    server {
        listen 80;

        server_name _;

        location / {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

echo "Создаю docker-compose.yml..."

cat > docker-compose.yml << 'EOF'
services:
  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: realestate
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    restart: unless-stopped
    env_file:
      - .env
    depends_on:
      - db
    ports:
      - "8000:8000"

  # telegram-bot:
  #   build: ./telegram-bot
  #   restart: unless-stopped
  #   env_file:
  #     - .env
  #   depends_on:
  #     - backend

volumes:
  db_data:
EOF

echo "Создаю .env.example..."

cat > .env.example << 'EOF'
ENVIRONMENT=local
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/realestate
SECRET_KEY=change_me_super_secret_key
EOF

echo "Создаю .gitignore..."

cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
*.pyo
*.pyd
.env.*
.venv/
venv/
.idea/
.vscode/
dist/
build/
db_data/
EOF

echo "Создаю README.md..."

cat > README.md << 'EOF'
# Real Estate Tinder

Monorepo for:
- backend (FastAPI + PostgreSQL)
- telegram-bot (future)
- web frontend (future)

## Quick start (local)

```bash
cp .env.example .env
docker compose build
docker compose up
