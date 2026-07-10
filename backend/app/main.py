"""FastAPI entrypoint: CORS, table creation, and routers for both modes."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import Base, engine
from app import models  # noqa: F401 (register models on Base)
from app.routers import interactions, chat

app = FastAPI(
    title="HCP CRM — AI Agent API",
    description="AI-first CRM for pharma field reps. Log HCP interactions via form or chat.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Create tables if they don't exist (simple demo migration).
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "model": settings.groq_model}


app.include_router(interactions.router)
app.include_router(chat.router)
