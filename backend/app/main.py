from fastapi import FastAPI

from .config import settings
from .api.routes_users import router as users_router
from .api.routes_listings import router as listings_router
from .api.routes_feed import router as feed_router
from .db import init_db  # 👈 добавили


app = FastAPI(
    title="Real Estate Tinder API",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    # импортируем модели, чтобы они зарегистрировались в Base
    from . import models  # noqa: F401
    init_db()


app.include_router(users_router)
app.include_router(listings_router)
app.include_router(feed_router)


@app.get("/health")
async def health():
    return {"status": "ok", "environment": settings.environment}
