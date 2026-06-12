"""Smoke test — validates API contract without external network calls."""

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)

    health_response = client.get("/health")
    assert health_response.status_code == 200, health_response.text
    assert health_response.json() == {"status": "ok"}

    ask_response = client.post("/ask", json={"question": "What is Phase 0?"})
    assert ask_response.status_code == 200, ask_response.text

    payload = ask_response.json()
    for field in ["answer", "confidence", "status", "trace_id", "citations"]:
        assert field in payload, f"Missing field: {field}"

    assert isinstance(payload["answer"], str) and payload["answer"]
    assert isinstance(payload["confidence"], (int, float))
    assert isinstance(payload["status"], str) and payload["status"]
    assert isinstance(payload["trace_id"], str) and payload["trace_id"]
    assert isinstance(payload["citations"], list)

    print("Smoke test passed.")


if __name__ == "__main__":
    main()
