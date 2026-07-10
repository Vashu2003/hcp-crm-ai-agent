"""Tests for run_agent robustness: it must survive a tool-calling loop and still
return a useful reply (the last tool result) instead of hanging or erroring."""

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.errors import GraphRecursionError

from app.agent import graph as graph_mod


class _FakeGraph:
    """Yields pre-baked states via .stream(); optionally raises like a real
    GraphRecursionError after exhausting them (to simulate a looping model)."""

    def __init__(self, states, raise_at_end=False):
        self.states = states
        self.raise_at_end = raise_at_end

    def stream(self, _inp, _config=None, stream_mode=None):
        for s in self.states:
            yield s
        if self.raise_at_end:
            raise GraphRecursionError("Recursion limit reached")


def _toolcall_msg(name):
    return AIMessage(content="", tool_calls=[{"name": name, "args": {}, "id": "call_1"}])


def test_run_agent_falls_back_to_tool_result_when_model_loops(monkeypatch):
    states = [
        {
            "messages": [
                HumanMessage(content="report please"),
                _toolcall_msg("generate_summary_report"),
                ToolMessage(content="REPORT TEXT", tool_call_id="call_1"),
            ]
        }
    ]
    monkeypatch.setattr(graph_mod, "get_graph", lambda: _FakeGraph(states, raise_at_end=True))
    out = graph_mod.run_agent("report please")
    assert out["reply"] == "REPORT TEXT"  # fell back to tool result despite the loop
    assert out["tool_calls"] == ["generate_summary_report"]


def test_run_agent_prefers_final_ai_message(monkeypatch):
    states = [
        {
            "messages": [
                HumanMessage(content="search"),
                _toolcall_msg("search_interactions"),
                ToolMessage(content="found 2", tool_call_id="call_1"),
                AIMessage(content="Here are your 2 interactions."),
            ]
        }
    ]
    monkeypatch.setattr(graph_mod, "get_graph", lambda: _FakeGraph(states))
    out = graph_mod.run_agent("search")
    assert out["reply"] == "Here are your 2 interactions."
    assert out["tool_calls"] == ["search_interactions"]  # de-duplicated
