from fastapi.testclient import TestClient

from app.data import clear_dataset
from app.main import app
from app.schemas import ParserOutput


client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stats_returns_404_without_uploaded_dataset() -> None:
    clear_dataset()

    response = client.get("/data/stats")

    assert response.status_code == 404


def test_upload_csv_and_get_stats() -> None:
    clear_dataset()
    csv_content = "name,score\nAlice,10\nBob,20\n"

    upload_response = client.post(
        "/data/upload",
        files={"file": ("scores.csv", csv_content, "text/csv")},
    )

    assert upload_response.status_code == 200
    assert upload_response.json()["rows"] == 2
    assert upload_response.json()["columns"] == ["name", "score"]
    assert "name" in upload_response.json()["dtypes"]
    assert upload_response.json()["dtypes"]["score"] == "int64"

    stats_response = client.get("/data/stats")

    assert stats_response.status_code == 200
    assert stats_response.json()["score"]["mean"] == 15.0


def test_upload_rejects_non_csv_file() -> None:
    response = client.post(
        "/data/upload",
        files={"file": ("scores.txt", "score\n10\n", "text/plain")},
    )

    assert response.status_code == 400


def test_ask_ai_returns_answer(monkeypatch) -> None:
    clear_dataset()
    client.post(
        "/data/upload",
        files={"file": ("scores.csv", "name,score\nAlice,10\nBob,20\n", "text/csv")},
    )

    class FakeChain:
        def run(self, data):
            return ParserOutput(answer=f"Test answer for: {data.question}")

    monkeypatch.setattr("app.main.ai_chain", FakeChain())

    response = client.post("/ai/ask", json={"question": "Vad ar medelvardet?"})

    assert response.status_code == 200
    assert response.json() == {
        "question": "Vad ar medelvardet?",
        "answer": "Test answer for: Vad ar medelvardet?",
        "model": "HuggingFaceTB/SmolLM2-135M-Instruct",
    }


def test_ask_ai_rejects_empty_question() -> None:
    response = client.post("/ai/ask", json={"question": "   "})

    assert response.status_code == 400


def test_ask_ai_requires_uploaded_dataset() -> None:
    clear_dataset()

    response = client.post("/ai/ask", json={"question": "Vad visar datat?"})

    assert response.status_code == 400
