"""Tests for the 5 LangGraph tools (invoked directly; LLM mocked)."""

from app.agent.tools import (
    log_interaction,
    edit_interaction,
    search_interactions,
    schedule_followup,
    generate_summary_report,
)


def test_log_interaction_tool_returns_summary():
    out = log_interaction.invoke({"hcp_name": "Dr. Tool", "raw_notes": "Discussed TestDrug."})
    assert "Logged interaction" in out
    assert "Dr. Tool" in out


def test_edit_interaction_tool_missing_id():
    out = edit_interaction.invoke({"interaction_id": 4242})
    assert "No interaction found" in out


def test_search_interactions_tool_finds_logged():
    log_interaction.invoke({"hcp_name": "Dr. Search", "raw_notes": "notes"})
    out = search_interactions.invoke({"hcp_name": "Search"})
    assert "Dr. Search" in out


def test_schedule_followup_tool_uses_llm_when_no_action():
    log_interaction.invoke({"hcp_name": "Dr. Follow", "raw_notes": "notes"})
    out = schedule_followup.invoke({"hcp_name": "Dr. Follow", "due_date": "2026-09-01"})
    assert "Scheduled follow-up" in out


def test_schedule_followup_tool_no_hcp():
    out = schedule_followup.invoke({"hcp_name": "Nobody", "action": "x"})
    assert "No HCP found" in out


def test_generate_summary_report_tool():
    log_interaction.invoke({"hcp_name": "Dr. Report", "raw_notes": "notes"})
    out = generate_summary_report.invoke({"hcp_name": "Report"})
    assert "AI-generated text" in out
