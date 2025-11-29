from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..deps import get_db
from ..models.lead import Lead
from ..schemas import LeadCreate, LeadRead

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("/", response_model=LeadRead)
def create_lead(
    lead_in: LeadCreate,
    db: Session = Depends(get_db),
):
    """
    Создать лид: арендатор заинтересовался конкретным объявлением.
    """
    lead = Lead(
        tenant_id=lead_in.tenant_id,
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
    tenant_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Лиды, созданные этим арендатором (он куда-то откликался).
    """
    leads = (
        db.query(Lead)
        .filter(Lead.tenant_id == tenant_id)
        .order_by(Lead.created_at.desc())
        .all()
    )
    return leads


@router.get("/for-me", response_model=list[LeadRead])
def list_leads_for_owner(
    owner_id: int = Query(...),
    db: Session = Depends(get_db),
):
    """
    Лиды по объявлениям этого владельца/агента.
    """
    leads = (
        db.query(Lead)
        .filter(Lead.owner_id == owner_id)
        .order_by(Lead.created_at.desc())
        .all()
    )
    return leads
