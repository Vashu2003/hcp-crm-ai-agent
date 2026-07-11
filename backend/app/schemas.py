from datetime import date as _date, datetime as _datetime
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict

# `date`/`datetime` are aliased above because a Pydantic field is literally named
# `date`; without the alias the field name shadows the type in its own annotation
# and Pydantic resolves the type to None.


# ---------- HCP ----------
class HCPBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    organization: Optional[str] = None
    notes: Optional[str] = None


class HCPOut(HCPBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: Optional[_datetime] = None


# ---------- Interaction ----------
class InteractionCreate(BaseModel):
    """Form-mode payload. hcp_name lets the form create/find an HCP by name."""

    hcp_name: str
    specialty: Optional[str] = None
    organization: Optional[str] = None
    rep_name: Optional[str] = None
    date: Optional[_date] = None
    channel: Optional[str] = None  # in-person / call / virtual
    product_discussed: Optional[str] = None
    raw_notes: str


class InteractionUpdate(BaseModel):
    rep_name: Optional[str] = None
    date: Optional[_date] = None
    channel: Optional[str] = None
    product_discussed: Optional[str] = None
    raw_notes: Optional[str] = None


class InteractionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hcp_id: int
    rep_name: Optional[str] = None
    date: Optional[_date] = None
    channel: Optional[str] = None
    product_discussed: Optional[str] = None
    raw_notes: Optional[str] = None
    llm_summary: Optional[str] = None
    extracted_entities: Optional[Any] = None
    sentiment: Optional[str] = None
    created_at: Optional[_datetime] = None
    updated_at: Optional[_datetime] = None
    hcp: Optional[HCPOut] = None


# ---------- FollowUp ----------
class FollowUpOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hcp_id: int
    interaction_id: Optional[int] = None
    due_date: Optional[_date] = None
    action: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[_datetime] = None
    hcp: Optional[HCPOut] = None


class FollowUpUpdate(BaseModel):
    status: Optional[str] = None  # pending / done / cancelled
    due_date: Optional[_date] = None
    action: Optional[str] = None


# ---------- Chat ----------
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []  # [{role: "user"|"assistant", content: str}]
    # The interaction currently shown in the form, so "correct it"/"change that" edits work.
    current_interaction_id: Optional[int] = None


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[str] = []  # names of tools the agent invoked (for UI transparency)
    # The interaction the agent just created/edited, so the UI form can auto-fill from chat.
    interaction: Optional[InteractionOut] = None
