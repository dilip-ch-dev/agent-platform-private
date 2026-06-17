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

    demo_response = client.get("/contextdiff/demo")
    assert demo_response.status_code == 200, demo_response.text
    demo_payload = demo_response.json()
    assert demo_payload["status"] == "BLOCK"
    assert demo_payload["summary"]["changed_statements"] >= 1
    assert demo_payload["summary"]["affected_queries"] >= 1
    assert demo_payload["summary"]["stale_retrievals"] >= 1
    assert "Release status: BLOCK" in demo_payload["html_report"]

    print("Smoke test passed.")


if __name__ == "__main__":
    main()
