"""Chat-mode endpoint: natural language -> LangGraph agent -> tools."""

from fastapi import APIRouter

from app.schemas import ChatRequest, ChatResponse
from app.agent.graph import run_agent

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    result = run_agent(payload.message, payload.history)
    return ChatResponse(reply=result["reply"], tool_calls=result["tool_calls"])
