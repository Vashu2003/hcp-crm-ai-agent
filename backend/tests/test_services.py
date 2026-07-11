"""Unit tests for the shared service layer (LLM mocked in conftest)."""

from datetime import date

from app.models import HCP, Interaction, FollowUp
from app.services import (
    get_or_create_hcp,
    log_interaction_service,
    edit_interaction_service,
    search_interactions_service,
    schedule_followup_service,
)


def test_get_or_create_hcp_creates_then_reuses(db):
    h1 = get_or_create_hcp(db, "Dr. Alice", specialty="Oncology")
    db.commit()
    h2 = get_or_create_hcp(db, "dr. alice")  # case-insensitive match
    assert h1.id == h2.id
    assert db.query(HCP).count() == 1


def test_log_interaction_runs_extraction_and_persists(db):
    i = log_interaction_service(db, hcp_name="Dr. Test", raw_notes="Met and discussed TestDrug.")
    assert i.id is not None
    assert i.llm_summary == "Test summary of the interaction."
    assert i.sentiment == "positive"
    assert i.product_discussed == "TestDrug"
    assert i.extracted_entities["key_topics"] == ["efficacy", "dosing"]
    # HCP auto-created
    assert db.query(HCP).filter(HCP.name == "Dr. Test").count() == 1


def test_log_interaction_autocreates_followup_when_action_present(db):
    log_interaction_service(db, hcp_name="Dr. Test", raw_notes="notes")
    # FAKE_EXTRACTION has follow_up_action set -> a follow-up should be created
    assert db.query(FollowUp).count() == 1


def test_edit_interaction_recomputes_on_notes_change(db):
    i = log_interaction_service(db, hcp_name="Dr. Test", raw_notes="old")
    i.llm_summary = "stale"
    db.commit()
    updated = edit_interaction_service(db, i.id, raw_notes="new notes", channel="call")
    assert updated.llm_summary == "Test summary of the interaction."  # recomputed
    assert updated.channel == "call"


def test_edit_interaction_missing_returns_none(db):
    assert edit_interaction_service(db, 9999, raw_notes="x") is None


def test_edit_interaction_keeps_date_on_unparseable(db):
    # Regression: an unparseable date must NOT wipe the stored date.
    i = log_interaction_service(db, hcp_name="Dr. Test", raw_notes="a", interaction_date="2026-05-01")
    original = i.date
    assert original == date(2026, 5, 1)
    updated = edit_interaction_service(db, i.id, date="next Tuesday")
    assert updated.date == original


def test_search_filters_by_hcp_and_sentiment(db):
    log_interaction_service(db, hcp_name="Dr. One", raw_notes="a")
    log_interaction_service(db, hcp_name="Dr. Two", raw_notes="b")
    results = search_interactions_service(db, hcp_name="One")
    assert len(results) == 1
    assert results[0].hcp.name == "Dr. One"

    # Multi-word query must match non-contiguously: "Dr. One" -> "Dr. One"
    assert len(search_interactions_service(db, hcp_name="Dr. One")) == 1

    pos = search_interactions_service(db, sentiment="positive")
    assert len(pos) == 2  # both mocked as positive


def test_search_matches_name_non_contiguously(db):
    # Regression: "Dr. Sharma" must find "Dr. Anita Sharma".
    log_interaction_service(db, hcp_name="Dr. Anita Sharma", raw_notes="a")
    assert len(search_interactions_service(db, hcp_name="Dr. Sharma")) == 1
    assert len(search_interactions_service(db, hcp_name="Sharma")) == 1


def test_schedule_followup_requires_existing_hcp(db):
    assert schedule_followup_service(db, hcp_name="Ghost", action="x") is None
    log_interaction_service(db, hcp_name="Dr. Real", raw_notes="a")
    fu = schedule_followup_service(db, hcp_name="Dr. Real", due_date="2026-08-01", action="Call back")
    assert fu is not None
    assert fu.due_date == date(2026, 8, 1)
    assert fu.action == "Call back"
