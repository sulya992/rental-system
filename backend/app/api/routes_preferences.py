from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..deps import get_db
from ..models.preferences import TenantPreference
from ..schemas import TenantPreferenceCreate, TenantPreferenceRead

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/", response_model=TenantPreferenceRead | None)
def get_preferences(
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    pref = (
        db.query(TenantPreference)
        .filter(TenantPreference.user_id == user_id)
        .first()
    )
    return pref


@router.post("/", response_model=TenantPreferenceRead)
def upsert_preferences(
    pref_in: TenantPreferenceCreate,
    db: Session = Depends(get_db),
):
    pref = (
        db.query(TenantPreference)
        .filter(TenantPreference.user_id == pref_in.user_id)
        .first()
    )

    if pref is None:
        pref = TenantPreference(user_id=pref_in.user_id)

    # обновляем поля из запроса
    for field, value in pref_in.model_dump(exclude={"user_id"}).items():
        setattr(pref, field, value)

    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref
