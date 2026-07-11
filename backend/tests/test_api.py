"""API-level tests for the Form-mode REST endpoints (LLM mocked)."""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_and_get_interaction(client):
    r = client.post(
        "/api/interactions",
        json={"hcp_name": "Dr. API", "raw_notes": "Discussed TestDrug in person.", "channel": "in-person"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["llm_summary"] == "Test summary of the interaction."
    assert body["sentiment"] == "positive"
    iid = body["id"]

    r2 = client.get(f"/api/interactions/{iid}")
    assert r2.status_code == 200
    assert r2.json()["id"] == iid
    assert r2.json()["hcp"]["name"] == "Dr. API"


def test_list_and_filter_interactions(client):
    client.post("/api/interactions", json={"hcp_name": "Dr. Alpha", "raw_notes": "a"})
    client.post("/api/interactions", json={"hcp_name": "Dr. Beta", "raw_notes": "b"})
    r = client.get("/api/interactions")
    assert r.status_code == 200
    assert len(r.json()) == 2
    r2 = client.get("/api/interactions", params={"hcp_name": "Alpha"})
    assert len(r2.json()) == 1


def test_update_interaction(client):
    iid = client.post("/api/interactions", json={"hcp_name": "Dr. Patch", "raw_notes": "old"}).json()["id"]
    r = client.patch(f"/api/interactions/{iid}", json={"channel": "call", "raw_notes": "new"})
    assert r.status_code == 200
    assert r.json()["channel"] == "call"


def test_update_missing_interaction_404(client):
    r = client.patch("/api/interactions/9999", json={"channel": "call"})
    assert r.status_code == 404


def test_list_hcps_and_followups(client):
    client.post("/api/interactions", json={"hcp_name": "Dr. List", "raw_notes": "x"})
    assert len(client.get("/api/hcps").json()) == 1
    # log_interaction auto-creates a follow-up (mock has follow_up_action)
    followups = client.get("/api/followups").json()
    assert len(followups) >= 1
    assert followups[0]["hcp"]["name"] == "Dr. List"  # hcp nested for the UI


def test_mark_followup_done(client):
    client.post("/api/interactions", json={"hcp_name": "Dr. FU", "raw_notes": "x"})
    fid = client.get("/api/followups").json()[0]["id"]
    r = client.patch(f"/api/followups/{fid}", json={"status": "done"})
    assert r.status_code == 200
    assert r.json()["status"] == "done"
    assert client.patch("/api/followups/9999", json={"status": "done"}).status_code == 404
