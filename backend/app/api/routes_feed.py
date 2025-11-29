from fastapi import APIRouter

router = APIRouter(prefix="/feed", tags=["feed"])


@router.get("/next")
async def get_next_listing():
    # Stub endpoint for now
    return {"detail": "no listings yet"}
