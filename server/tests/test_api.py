from api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_endpoint_smoke(monkeypatch):
    calls = {"ingest": False}

    from api.routes import ingest as ingest_routes

    def fake_ingest():
        calls["ingest"] = True

    monkeypatch.setattr(ingest_routes, "run_full_ingest", fake_ingest, raising=True)

    resp = client.post("/ingest")
    assert resp.status_code == 200
    assert resp.json()["message"].startswith("Ingestion process")
    assert calls["ingest"] is True


def test_process_endpoint_smoke(monkeypatch):
    calls = {"process": False}

    from api.routes import process as process_routes

    def fake_process():
        calls["process"] = True

    monkeypatch.setattr(process_routes, "run_build_graph", fake_process, raising=True)

    resp = client.post("/process")
    assert resp.status_code == 200
    assert "Graph built" in resp.json()["message"]
    assert calls["process"] is True


def test_chat_endpoint_uses_openai_and_returns_content(monkeypatch):
    from api.routes import llm as chat_routes

    calls = {"called": False, "input": None}

    class FakeChoiceText:
        def __init__(self, text: str):
            self.text = text

    class FakeOutputItem:
        def __init__(self, text: str):
            self.content = [FakeChoiceText(text)]

    class FakeResponse:
        def __init__(self, text: str):
            self.output = [FakeOutputItem(text)]

    class FakeOpenAIClient:
        class Responses:
            @staticmethod
            def create(**kwargs):
                calls["called"] = True
                calls["input"] = kwargs["input"]
                return FakeResponse("fake answer from model")

        responses = Responses()

    monkeypatch.setattr(chat_routes, "openai_client", FakeOpenAIClient(), raising=True)

    resp = client.post("/chat", data={"message": "What is Bulbasaur?"})
    assert resp.status_code == 200
    body = resp.json()
    assert "content" in body
    assert body["content"] == "fake answer from model"
    assert calls["called"] is True

    assert isinstance(calls["input"], list)
    assert any(
        "Bulbasaur" in item["content"]
        for item in calls["input"]
        if item["role"] == "user"
    )


def test_graph_endpoint_404_when_missing(tmp_path, monkeypatch):
    from api.routes import graph as graph_routes

    fake_graph_json = tmp_path / "graph.json"
    monkeypatch.setattr(graph_routes, "GRAPH_JSON", fake_graph_json, raising=True)

    resp = client.get("/graph")
    assert resp.status_code == 404
    assert "Graph not built yet" in resp.json()["detail"]


def test_graph_endpoint_returns_graph_json(tmp_path, monkeypatch):
    from api.routes import graph as graph_routes

    fake_graph_json = tmp_path / "graph.json"
    fake_graph_json.write_text(
        '{"pokemon_nodes":[{"name":"Bulbasaur","generation":1,"primary_type":"Grass","secondary_type":"Poison"}],'
        '"type_nodes":[{"name":"Grass"}],'
        '"pokemon_type_edges":[{"from_pokemon":"Bulbasaur","to_type":"Grass"}],'
        '"evolution_edges":[],'
        '"mentions_edges":[]}',
        encoding="utf-8",
    )

    monkeypatch.setattr(graph_routes, "GRAPH_JSON", fake_graph_json, raising=True)

    resp = client.get("/graph")
    assert resp.status_code == 200
    data = resp.json()
    assert data["pokemon_nodes"][0]["name"] == "Bulbasaur"
    assert data["type_nodes"][0]["name"] == "Grass"


def test_logs_endpoint_returns_parsed_records(tmp_path, monkeypatch):
    from api.routes import logs as logs_routes

    fake_log_path = tmp_path / "eval.jsonl"
    fake_log_path.write_text(
        '{"timestamp":"2025-11-24T17:26:15.686778+00:00","query":"What is Pikachu all about?","answer":"A","retrieved_context":"ctx","evaluation":{"grounded_in_graph":true,"latency_ms":null},"focused_pokemon":{"name":"Pikachu"}}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(logs_routes, "LOG_PATH", fake_log_path, raising=True)

    resp = client.get("/logs")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["query"] == "What is Pikachu all about?"
    assert data[0]["focused_pokemon"]["name"] == "Pikachu"
