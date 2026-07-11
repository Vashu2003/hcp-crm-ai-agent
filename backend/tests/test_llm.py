"""Tests for summarize_and_extract resilience. Note: the autouse _mock_llm fixture
patches services.summarize_and_extract and tools.get_llm, but NOT llm.get_llm — so
here we exercise the real summarize_and_extract and patch llm.get_llm directly."""

import json

from app.agent import llm as llm_mod


class _Resp:
    def __init__(self, content):
        self.content = content


class _LLM:
    def __init__(self, content=None, raise_exc=None):
        self._content = content
        self._raise = raise_exc

    def invoke(self, _prompt):
        if self._raise:
            raise self._raise
        return _Resp(self._content)


def test_extract_falls_back_to_raw_notes_on_api_error(monkeypatch):
    monkeypatch.setattr(llm_mod, "get_llm", lambda: _LLM(raise_exc=RuntimeError("groq down")))
    out = llm_mod.summarize_and_extract("Met Dr. X about DrugY.")
    assert out["summary"] == "Met Dr. X about DrugY."  # notes preserved, not lost
    assert out["sentiment"] == "neutral"
    assert out["products"] == []


def test_extract_parses_valid_json(monkeypatch):
    payload = {
        "summary": "s", "hcp_name": "Dr. X", "specialty": None, "products": ["DrugY"],
        "key_topics": ["t"], "sentiment": "positive", "samples_given": None,
        "follow_up_date": None, "follow_up_action": None,
    }
    monkeypatch.setattr(llm_mod, "get_llm", lambda: _LLM(content=json.dumps(payload)))
    out = llm_mod.summarize_and_extract("notes")
    assert out["products"] == ["DrugY"]
    assert out["sentiment"] == "positive"


def test_extract_handles_code_fenced_json(monkeypatch):
    fenced = '```json\n{"summary":"s","sentiment":"positive","products":[]}\n```'
    monkeypatch.setattr(llm_mod, "get_llm", lambda: _LLM(content=fenced))
    out = llm_mod.summarize_and_extract("notes")
    assert out["sentiment"] == "positive"
