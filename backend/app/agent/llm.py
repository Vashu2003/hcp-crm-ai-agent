"""Groq LLM client + the shared summarization/entity-extraction helper.

Both the structured Form flow and the conversational Chat flow call
`summarize_and_extract`, so the two input modes share the exact same AI logic.
"""

import json
from functools import lru_cache

from langchain_groq import ChatGroq

from app.config import settings
from app.agent.prompts import EXTRACTION_PROMPT


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.2) -> ChatGroq:
    """Return a cached ChatGroq client bound to the configured model."""
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=temperature,
    )


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        # remove ```json ... ``` or ``` ... ```
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3]
    return text.strip()


def summarize_and_extract(raw_notes: str) -> dict:
    """Run LLM summarization + entity extraction on raw interaction notes.

    Returns a dict with keys: summary, hcp_name, specialty, products,
    key_topics, sentiment, samples_given, follow_up_date, follow_up_action.
    Falls back to a minimal dict if the model returns unparseable output.
    """
    def _fallback(summary: str) -> dict:
        return {
            "summary": summary,
            "hcp_name": None,
            "specialty": None,
            "products": [],
            "key_topics": [],
            "sentiment": "neutral",
            "samples_given": None,
            "follow_up_date": None,
            "follow_up_action": None,
        }

    # Any LLM/API failure (rate limit, network) must NOT lose the rep's notes: fall
    # back to persisting the raw notes as the summary rather than raising.
    try:
        resp = get_llm().invoke(EXTRACTION_PROMPT.replace("{raw_notes}", raw_notes))
        content = resp.content if isinstance(resp.content, str) else str(resp.content)
    except Exception:
        return _fallback(raw_notes.strip()[:500])

    try:
        return json.loads(_strip_code_fence(content))
    except (json.JSONDecodeError, ValueError):
        return _fallback(content.strip()[:500] or raw_notes.strip()[:500])
