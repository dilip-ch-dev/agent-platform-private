"""Gradio demo UI.

Calls FastAPI ``/ask`` over HTTP — never imports pipeline code directly
(CLAUDE.md boundary rule). Skin the title/description per problem statement.
"""

import json

import gradio as gr
import httpx

from app.config import cfg

API_URL = cfg.api_url.rstrip("/")


def ask_agent(question: str) -> tuple[str, str, float, str, str, str]:
    if not question.strip():
        return "Please enter a question.", "blocked", 0.0, "", "[]", "[]"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(f"{API_URL}/ask", json={"question": question})
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        return f"API request failed: {exc}", "blocked", 0.0, "", "[]", "[]"

    return (
        payload.get("answer", ""),
        payload.get("status", ""),
        float(payload.get("confidence", 0.0)),
        payload.get("trace_id", ""),
        json.dumps(payload.get("citations", []), indent=2),
        json.dumps(payload.get("flags", []), indent=2),
    )


demo = gr.Interface(
    fn=ask_agent,
    inputs=gr.Textbox(label="Question", placeholder="Ask the agent a question..."),
    outputs=[
        gr.Textbox(label="Answer"),
        gr.Textbox(label="Status"),
        gr.Number(label="Confidence"),
        gr.Textbox(label="Trace ID"),
        gr.Textbox(label="Citations", lines=6),
        gr.Textbox(label="Flags", lines=2),
    ],
    title="Buildathon Agent Platform Demo",
    description="Calls FastAPI /ask over HTTP. PII redaction + injection blocking active.",
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
