from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..models.lead import Lead
from ..models.user import User
from ..schemas import LeadCreate, LeadRead

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/", response_model=LeadRead)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать лид от лица текущего пользователя (арендатора).
    Обычно это делает /feed/action, но можно и вручную.
    """
    tenant_id = current_user.id

    lead = Lead(
        tenant_id=tenant_id,
        listing_id=lead_in.listing_id,
        owner_id=lead_in.owner_id,
        status=lead_in.status or "new",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


@router.get("/my", response_model=list[LeadRead])
def list_my_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Лиды текущего пользователя как арендатора.
    """
    leads = (
        db.query(Lead)
        .filter(Lead.tenant_id == current_user.id)
        .order_by(Lead.created_at.desc())
        .all()
    )
    return leads


@router.get("/for-me", response_model=list[LeadRead])
def list_leads_for_owner(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Лиды по объявлениям текущего владельца/агента.
    """
    if current_user.role not in ("landlord", "agent", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners/agents/admin can view leads for them",
        )

    leads = (
        db.query(Lead)
        .filter(Lead.owner_id == current_user.id)
        .order_by(Lead.created_at.desc())
        .all()
    )
    return leads
