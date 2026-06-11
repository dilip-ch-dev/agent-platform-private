import json
import os

import gradio as gr
import httpx
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")


def ask_agent(question: str) -> tuple[str, str, float, str, str]:
    if not question.strip():
        return "Please enter a question.", "blocked", 0.0, "", "[]"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_URL}/ask",
                json={"question": question},
            )
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        return f"API request failed: {exc}", "blocked", 0.0, "", "[]"

    citations = json.dumps(payload.get("citations", []), indent=2)
    return (
        payload.get("answer", ""),
        payload.get("status", ""),
        float(payload.get("confidence", 0.0)),
        payload.get("trace_id", ""),
        citations,
    )


demo = gr.Interface(
    fn=ask_agent,
    inputs=gr.Textbox(label="Question", placeholder="Ask the agent a question..."),
    outputs=[
        gr.Textbox(label="Answer"),
        gr.Textbox(label="Status"),
        gr.Number(label="Confidence"),
        gr.Textbox(label="Trace ID"),
        gr.Textbox(label="Citations", lines=8),
    ],
    title="Buildathon Agent Platform Demo",
    description="Gradio UI calling FastAPI /ask over HTTP.",
)

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
