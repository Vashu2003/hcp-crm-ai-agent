"""Pytest setup: SQLite test DB + mocked Groq LLM so tests run offline & fast.

We point DATABASE_URL at a temporary SQLite file BEFORE importing any app module,
so app.config.settings and the SQLAlchemy engine bind to SQLite instead of Postgres.
The Groq LLM is mocked at the two seams it's used: services.summarize_and_extract
and agent.tools.get_llm.
"""

import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(tempfile.gettempdir(), 'hcp_test.db')}"
os.environ["GROQ_API_KEY"] = "test-key-not-used"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, engine, SessionLocal  # noqa: E402
from app import services  # noqa: E402
from app.agent import tools as tools_module  # noqa: E402
from app.main import app  # noqa: E402


FAKE_EXTRACTION = {
    "summary": "Test summary of the interaction.",
    "hcp_name": "Dr. Test",
    "specialty": "Cardiology",
    "products": ["TestDrug"],
    "key_topics": ["efficacy", "dosing"],
    "sentiment": "positive",
    "samples_given": "2 boxes",
    "follow_up_date": None,
    "follow_up_action": "Send clinical data.",
}


class _FakeLLMResponse:
    def __init__(self, content):
        self.content = content


class _FakeLLM:
    def invoke(self, _prompt):
        return _FakeLLMResponse("AI-generated text for report / next-best-action.")


@pytest.fixture(autouse=True)
def _mock_llm(monkeypatch):
    """Replace the LLM calls everywhere they're used."""
    monkeypatch.setattr(services, "summarize_and_extract", lambda notes: dict(FAKE_EXTRACTION))
    monkeypatch.setattr(tools_module, "get_llm", lambda: _FakeLLM())


@pytest.fixture(autouse=True)
def _fresh_db():
    """Drop + recreate all tables before every test for isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)
