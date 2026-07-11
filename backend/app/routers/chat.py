"""Chat-mode endpoint: natural language -> LangGraph agent -> tools."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Interaction
from app.schemas import ChatRequest, ChatResponse
from app.agent.graph import run_agent

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    result = run_agent(payload.message, payload.history, payload.current_interaction_id)

    # If the agent logged/edited an interaction, return it so the UI form auto-fills.
    interaction = None
    if result.get("interaction_id"):
        interaction = db.get(Interaction, result["interaction_id"])

    return ChatResponse(
        reply=result["reply"],
        tool_calls=result["tool_calls"],
        interaction=interaction,
    )
