"""Form-mode REST endpoints (deterministic CRUD).

These reuse the SAME service layer the LangGraph tools call, so the structured
Form flow and the conversational Chat flow share summarization/extraction logic.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import HCP, Interaction, FollowUp
from app.schemas import (
    InteractionCreate,
    InteractionUpdate,
    InteractionOut,
    HCPOut,
    FollowUpOut,
)
from app.services import (
    log_interaction_service,
    edit_interaction_service,
    search_interactions_service,
    list_followups_service,
)

router = APIRouter(prefix="/api", tags=["interactions"])


@router.post("/interactions", response_model=InteractionOut)
def create_interaction(payload: InteractionCreate, db: Session = Depends(get_db)):
    """Form mode: log an interaction (runs LLM summary + entity extraction)."""
    interaction = log_interaction_service(
        db,
        hcp_name=payload.hcp_name,
        raw_notes=payload.raw_notes,
        rep_name=payload.rep_name,
        interaction_date=payload.date,
        channel=payload.channel,
        product_discussed=payload.product_discussed,
        specialty=payload.specialty,
        organization=payload.organization,
    )
    return interaction


@router.get("/interactions", response_model=list[InteractionOut])
def list_interactions(
    hcp_name: str | None = None,
    product: str | None = None,
    sentiment: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    db: Session = Depends(get_db),
):
    return search_interactions_service(
        db,
        hcp_name=hcp_name,
        product=product,
        sentiment=sentiment,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/interactions/{interaction_id}", response_model=InteractionOut)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).get(interaction_id)
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.patch("/interactions/{interaction_id}", response_model=InteractionOut)
def update_interaction(
    interaction_id: int, payload: InteractionUpdate, db: Session = Depends(get_db)
):
    interaction = edit_interaction_service(
        db,
        interaction_id,
        raw_notes=payload.raw_notes,
        rep_name=payload.rep_name,
        date=payload.date,
        channel=payload.channel,
        product_discussed=payload.product_discussed,
    )
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.get("/hcps", response_model=list[HCPOut])
def list_hcps(db: Session = Depends(get_db)):
    return db.query(HCP).order_by(HCP.name.asc()).all()


@router.get("/followups", response_model=list[FollowUpOut])
def list_followups(status: str | None = None, db: Session = Depends(get_db)):
    return list_followups_service(db, status=status)
