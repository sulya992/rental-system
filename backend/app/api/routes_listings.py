from fastapi import APIRouter

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("/")
async def list_listings():
    # Stub endpoint for now
    return []
