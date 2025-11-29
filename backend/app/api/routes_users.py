from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_me():
    # Stub endpoint for now
    return {"detail": "user endpoint stub"}
