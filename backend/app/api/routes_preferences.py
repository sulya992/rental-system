from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..models.preferences import TenantPreference
from ..models.user import User
from ..schemas import TenantPreferenceCreate, TenantPreferenceRead

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/", response_model=TenantPreferenceRead | None)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Предпочтения текущего пользователя (арендатора).
    """
    pref = (
        db.query(TenantPreference)
        .filter(TenantPreference.user_id == current_user.id)
        .first()
    )
    return pref


@router.post("/", response_model=TenantPreferenceRead)
def upsert_preferences(
    pref_in: TenantPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать или обновить предпочтения для текущего пользователя.
    """
    pref = (
        db.query(TenantPreference)
        .filter(TenantPreference.user_id == current_user.id)
        .first()
    )

    if pref is None:
        pref = TenantPreference(user_id=current_user.id)

    # обновляем поля из запроса (user_id игнорируем)
    for field, value in pref_in.model_dump(exclude={"user_id"}).items():
        setattr(pref, field, value)

    db.add(pref)
    db.commit()
    db.refresh(pref)
    return pref
