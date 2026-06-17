from __future__ import annotations

import json

import gradio as gr

from app.contextdiff.demo import run_seed_demo


def _run_demo() -> tuple[str, str, str]:
    report = run_seed_demo()
    summary = (
        f"Release status: {report.status}\n"
        f"Changed policy detected: {report.summary.changed_statements}\n"
        f"Affected queries identified: {report.summary.affected_queries}\n"
        f"Generated probes: {report.summary.generated_probes}\n"
        f"Stale source retrieved: {report.summary.stale_retrievals}\n"
        f"Blocks: {report.summary.block_count}"
    )
    table_rows = [
        [
            regression.status,
            regression.query.query_id,
            regression.query.question,
            ", ".join(regression.reason_codes),
            regression.old_answer,
            regression.new_answer,
        ]
        for regression in report.regressions
    ]
    table_markdown = (
        "| Status | Query | Question | Reasons | Old answer | New answer |\n"
    )
    table_markdown += "|---|---|---|---|---|---|\n"
    table_markdown += "\n".join(
        "| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |"
        for row in table_rows
    )
    payload = json.dumps(report.model_dump(mode="json"), indent=2)
    return summary, table_markdown, payload


with gr.Blocks(title="ContextDiff") as demo:
    gr.Markdown("# ContextDiff")
    gr.Markdown("Run the seeded policy regression gate.")
    run_button = gr.Button("Run canonical demo", variant="primary")
    status_output = gr.Textbox(label="Gate summary", lines=6)
    table_output = gr.Markdown(label="Regressions")
    json_output = gr.Code(label="JSON report", language="json")
    run_button.click(
        fn=_run_demo,
        inputs=[],
        outputs=[status_output, table_output, json_output],
    )
