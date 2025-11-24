from api.main import app
from fastapi.testclient import (  # type: ignore (local editor quirk, safe to ignore)
    TestClient,
)

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_endpoint_smoke(monkeypatch):
    calls = {"ingest": False, "process": False}

    from api.routes import ingest as api_main

    def fake_ingest():
        calls["ingest"] = True

    monkeypatch.setattr(api_main, "run_full_ingest", fake_ingest, raising=True)

    resp = client.post("/ingest")
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("Ingestion process")
    assert calls["ingest"] is True


def test_process_endpoint_smoke(monkeypatch):
    calls = {"process": False}

    from api.routes import process as api_main

    def fake_process():
        calls["process"] = True

    monkeypatch.setattr(api_main, "run_build_graph", fake_process, raising=True)

    resp = client.post("/process")
    assert resp.status_code == 200
    assert "Graph built" in resp.json()["message"]
    assert calls["process"] is True
