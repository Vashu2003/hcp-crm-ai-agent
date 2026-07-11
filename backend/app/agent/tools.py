"""The 5 LangGraph tools. Each opens its own DB session and delegates to the
service layer, so the tools stay thin and share logic with the Form flow.
"""

from typing import Optional

from langchain_core.tools import tool

from app.db import SessionLocal
from app.agent.llm import get_llm
from app.services import (
    log_interaction_service,
    edit_interaction_service,
    search_interactions_service,
    schedule_followup_service,
)


def _fmt_interaction(i) -> str:
    # Truncate the summary to keep tool output (fed back to the LLM) token-bounded.
    summary = (i.llm_summary or i.raw_notes or "")[:160]
    return (
        f"#{i.id} | {i.hcp.name if i.hcp else '?'} | {i.date} | "
        f"{i.channel or '-'} | product: {i.product_discussed or '-'} | "
        f"sentiment: {i.sentiment or '-'}\n    summary: {summary}"
    )


# --- Tool 1: Log Interaction (specified) ---
@tool
def log_interaction(
    hcp_name: str,
    raw_notes: str,
    rep_name: Optional[str] = None,
    date: Optional[str] = None,
    channel: Optional[str] = None,
    product_discussed: Optional[str] = None,
) -> str:
    """Log a new HCP interaction. Runs AI summarization + entity extraction
    (HCP name, specialty, products, sentiment, key topics, follow-up).
    `date` is YYYY-MM-DD; `channel` is one of in-person/call/virtual."""
    db = SessionLocal()
    try:
        i = log_interaction_service(
            db,
            hcp_name=hcp_name,
            raw_notes=raw_notes,
            rep_name=rep_name,
            interaction_date=date,
            channel=channel,
            product_discussed=product_discussed,
        )
        ents = i.extracted_entities or {}
        return (
            f"Logged interaction #{i.id} with {i.hcp.name}.\n"
            f"Summary: {i.llm_summary}\n"
            f"Sentiment: {i.sentiment} | Products: {ents.get('products')} | "
            f"Topics: {ents.get('key_topics')} | Follow-up: {ents.get('follow_up_date')}"
        )
    finally:
        db.close()


# --- Tool 2: Edit Interaction (specified) ---
@tool
def edit_interaction(
    interaction_id: int,
    raw_notes: Optional[str] = None,
    rep_name: Optional[str] = None,
    date: Optional[str] = None,
    channel: Optional[str] = None,
    product_discussed: Optional[str] = None,
) -> str:
    """Edit an existing interaction by id. If raw_notes are changed, the AI
    summary, entities and sentiment are recomputed."""
    db = SessionLocal()
    try:
        i = edit_interaction_service(
            db,
            interaction_id,
            raw_notes=raw_notes,
            rep_name=rep_name,
            date=date,
            channel=channel,
            product_discussed=product_discussed,
        )
        if not i:
            return f"No interaction found with id {interaction_id}."
        return f"Updated interaction #{i.id}. New summary: {i.llm_summary}"
    finally:
        db.close()


# --- Tool 3: Search / List Interactions ---
@tool
def search_interactions(
    hcp_name: Optional[str] = None,
    product: Optional[str] = None,
    sentiment: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> str:
    """Search past interactions by HCP name, product, sentiment
    (positive/neutral/negative), and/or date range (YYYY-MM-DD)."""
    db = SessionLocal()
    try:
        rows = search_interactions_service(
            db,
            hcp_name=hcp_name,
            product=product,
            sentiment=sentiment,
            date_from=date_from,
            date_to=date_to,
        )
        if not rows:
            return "No matching interactions found."
        return f"Found {len(rows)} interaction(s):\n" + "\n".join(_fmt_interaction(r) for r in rows)
    finally:
        db.close()


# --- Tool 4: Schedule Follow-up / Next-Best-Action ---
@tool
def schedule_followup(
    hcp_name: str,
    due_date: Optional[str] = None,
    action: Optional[str] = None,
) -> str:
    """Schedule a follow-up for an HCP. If no action text is given, the AI
    suggests a next-best-action from the HCP's recent interactions.
    `due_date` is YYYY-MM-DD."""
    db = SessionLocal()
    try:
        if not action:
            recent = search_interactions_service(db, hcp_name=hcp_name, limit=5)
            context = "\n".join(_fmt_interaction(r) for r in recent) or "No prior interactions."
            suggestion = get_llm().invoke(
                "You are a pharma sales strategist. Based on these recent interactions with "
                f"{hcp_name}, suggest ONE concise next-best-action (max 25 words).\n{context}"
            )
            action = (suggestion.content if isinstance(suggestion.content, str) else str(suggestion.content)).strip()

        fu = schedule_followup_service(db, hcp_name=hcp_name, due_date=due_date, action=action)
        if not fu:
            return f"No HCP found matching '{hcp_name}'. Log an interaction first."
        return f"Scheduled follow-up #{fu.id} for {hcp_name} on {fu.due_date or 'TBD'}: {fu.action}"
    finally:
        db.close()


# --- Tool 5: Generate Summary Report ---
@tool
def generate_summary_report(
    hcp_name: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> str:
    """Generate an LLM narrative report across interactions, optionally filtered
    by HCP name and/or date range (e.g. 'summarize last month with Dr. Sharma')."""
    db = SessionLocal()
    try:
        rows = search_interactions_service(
            db, hcp_name=hcp_name, date_from=date_from, date_to=date_to, limit=40
        )
        if not rows:
            return "No interactions found for that filter."
        corpus = "\n".join(_fmt_interaction(r) for r in rows)
        scope = f" with {hcp_name}" if hcp_name else ""
        report = get_llm().invoke(
            f"You are a pharma field-sales analyst. Write a concise activity report{scope} "
            f"based on the {len(rows)} interactions below. Cover: key HCPs, products discussed, "
            f"overall sentiment, notable outcomes, and recommended follow-ups. Use short paragraphs "
            f"and bullet points.\n\n{corpus}"
        )
        return report.content if isinstance(report.content, str) else str(report.content)
    finally:
        db.close()


ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    search_interactions,
    schedule_followup,
    generate_summary_report,
]
