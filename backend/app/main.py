from fastapi import FastAPI

from .config import settings
from .api.routes_users import router as users_router
from .api.routes_listings import router as listings_router
from .api.routes_feed import router as feed_router
from .api.routes_preferences import router as preferences_router
from .api.routes_favorites import router as favorites_router  
from .api.routes_leads import router as leads_router          
from .db import init_db
from .api.routes_auth import router as auth_router

app = FastAPI(
    title="Real Estate Tinder API",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(listings_router)
app.include_router(preferences_router)
app.include_router(favorites_router)
app.include_router(leads_router)
app.include_router(feed_router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "environment": settings.environment,
    }
