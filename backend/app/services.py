"""Core business logic shared by BOTH input modes.

The Form flow (routers/interactions.py) and the Chat flow (agent/tools.py)
both call these functions, so structured input and natural-language input
run through identical summarization/extraction and persistence logic.
"""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models import HCP, Interaction, FollowUp
from app.agent.llm import summarize_and_extract


def _parse_date(value) -> Optional[date]:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def get_or_create_hcp(
    db: Session,
    name: str,
    specialty: Optional[str] = None,
    organization: Optional[str] = None,
) -> HCP:
    """Find an HCP by (case-insensitive, whitespace-normalized) name or create one."""
    name = " ".join(name.split())  # collapse internal/edge whitespace
    hcp = db.query(HCP).filter(HCP.name.ilike(name)).first()
    if hcp:
        # backfill specialty/org if newly provided
        if specialty and not hcp.specialty:
            hcp.specialty = specialty
        if organization and not hcp.organization:
            hcp.organization = organization
        return hcp
    hcp = HCP(name=name, specialty=specialty, organization=organization)
    db.add(hcp)
    db.flush()  # assign id without committing
    return hcp


def log_interaction_service(
    db: Session,
    hcp_name: str,
    raw_notes: str,
    rep_name: Optional[str] = None,
    interaction_date=None,
    channel: Optional[str] = None,
    product_discussed: Optional[str] = None,
    specialty: Optional[str] = None,
    organization: Optional[str] = None,
) -> Interaction:
    """Create an interaction, running LLM summarization + entity extraction."""
    extraction = summarize_and_extract(raw_notes)

    # Prefer explicit specialty; else use what the LLM found.
    specialty = specialty or extraction.get("specialty")
    hcp = get_or_create_hcp(db, hcp_name, specialty, organization)

    products = extraction.get("products") or []
    product = product_discussed or (products[0] if products else None)

    interaction = Interaction(
        hcp_id=hcp.id,
        rep_name=rep_name,
        date=_parse_date(interaction_date) or date.today(),
        channel=channel,
        product_discussed=product,
        raw_notes=raw_notes,
        llm_summary=extraction.get("summary"),
        extracted_entities=extraction,
        sentiment=extraction.get("sentiment"),
    )
    db.add(interaction)
    db.flush()

    # If the LLM found a follow-up date/action, auto-create a follow-up.
    fu_date = _parse_date(extraction.get("follow_up_date"))
    fu_action = extraction.get("follow_up_action")
    if fu_date or fu_action:
        db.add(
            FollowUp(
                interaction_id=interaction.id,
                hcp_id=hcp.id,
                due_date=fu_date,
                action=fu_action,
                status="pending",
            )
        )
    db.commit()
    db.refresh(interaction)
    return interaction


def edit_interaction_service(db: Session, interaction_id: int, **fields) -> Optional[Interaction]:
    """Update an interaction; re-run extraction if raw_notes changed."""
    interaction = db.get(Interaction, interaction_id)
    if not interaction:
        return None

    if fields.get("raw_notes"):
        interaction.raw_notes = fields["raw_notes"]
        extraction = summarize_and_extract(fields["raw_notes"])
        interaction.llm_summary = extraction.get("summary")
        interaction.extracted_entities = extraction
        interaction.sentiment = extraction.get("sentiment")

    # Correct a mis-attributed HCP: re-link the interaction to the named HCP
    # (create it if new). A specialty-only edit updates the current HCP.
    hcp_name = fields.get("hcp_name")
    specialty = fields.get("specialty")
    organization = fields.get("organization")
    if hcp_name:
        hcp = get_or_create_hcp(db, hcp_name, specialty, organization)
        interaction.hcp_id = hcp.id
        if specialty:
            hcp.specialty = specialty
        if organization:
            hcp.organization = organization
    elif interaction.hcp and (specialty or organization):
        if specialty:
            interaction.hcp.specialty = specialty
        if organization:
            interaction.hcp.organization = organization

    for key in ("rep_name", "channel", "product_discussed"):
        if fields.get(key) is not None:
            setattr(interaction, key, fields[key])
    if fields.get("date") is not None:
        parsed = _parse_date(fields["date"])
        if parsed is not None:  # don't wipe a valid stored date on an unparseable input
            interaction.date = parsed

    db.commit()
    db.refresh(interaction)
    return interaction


def search_interactions_service(
    db: Session,
    hcp_name: Optional[str] = None,
    product: Optional[str] = None,
    sentiment: Optional[str] = None,
    date_from=None,
    date_to=None,
    limit: int = 50,
):
    q = db.query(Interaction)
    if hcp_name:
        # Match each word so "Dr. Sharma" finds "Dr. Anita Sharma" (non-contiguous).
        q = q.join(HCP)
        for token in hcp_name.split():
            q = q.filter(HCP.name.ilike(f"%{token}%"))
    if product:
        q = q.filter(Interaction.product_discussed.ilike(f"%{product}%"))
    if sentiment:
        q = q.filter(Interaction.sentiment.ilike(sentiment))
    df, dt = _parse_date(date_from), _parse_date(date_to)
    if df:
        q = q.filter(Interaction.date >= df)
    if dt:
        q = q.filter(Interaction.date <= dt)
    return q.order_by(Interaction.date.desc(), Interaction.id.desc()).limit(limit).all()


def schedule_followup_service(
    db: Session,
    hcp_name: str,
    due_date=None,
    action: Optional[str] = None,
    interaction_id: Optional[int] = None,
) -> Optional[FollowUp]:
    hcp = db.query(HCP).filter(HCP.name.ilike(f"%{hcp_name}%")).first()
    if not hcp:
        return None
    fu = FollowUp(
        hcp_id=hcp.id,
        interaction_id=interaction_id,
        due_date=_parse_date(due_date),
        action=action,
        status="pending",
    )
    db.add(fu)
    db.commit()
    db.refresh(fu)
    return fu


def list_followups_service(db: Session, status: Optional[str] = None):
    q = db.query(FollowUp)
    if status:
        q = q.filter(FollowUp.status.ilike(status))
    return q.order_by(FollowUp.due_date.asc().nullslast()).all()


def update_followup_service(
    db: Session, followup_id: int, status=None, due_date=None, action=None
) -> Optional[FollowUp]:
    fu = db.get(FollowUp, followup_id)
    if not fu:
        return None
    if status is not None:
        fu.status = status
    if due_date is not None:
        parsed = _parse_date(due_date)
        if parsed is not None:
            fu.due_date = parsed
    if action is not None:
        fu.action = action
    db.commit()
    db.refresh(fu)
    return fu
