from uuid import uuid4

from fastapi import FastAPI

from app.audit import AuditLogger
from app.config import cfg
from app.guardrails import injection, pii
from packages.contracts.schemas import (
    AgentRequest,
    AgentResponse,
    Citation,
    HealthResponse,
    Locator,
)

app = FastAPI(title="Buildathon Agent Platform", version="0.1.0")
audit = AuditLogger(cfg.audit_log_path)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/ask", response_model=AgentResponse)
def ask(request: AgentRequest) -> AgentResponse:
    trace_id = str(uuid4())

    # Input guardrails — always on redacted text from here on.
    redacted_question, pii_types = pii.redact(request.question)
    injection_score, flagged_spans = injection.score(redacted_question)

    flags = [f"pii:{t}" for t in pii_types]

    audit.log_event(
        trace_id,
        "ask_received",
        {
            "redacted_question": redacted_question,
            "pii_types": pii_types,
            "injection_score": injection_score,
        },
    )

    if injection.is_blocked(injection_score, cfg.injection_threshold, cfg.injection_mode):
        response = AgentResponse(
            answer="Request blocked by input guardrails.",
            status="blocked",
            confidence=0.0,
            trace_id=trace_id,
            citations=[],
            flags=[*flags, "injection"],
        )
        audit.log_event(
            trace_id,
            "ask_blocked",
            {"injection_score": injection_score, "flagged_spans": flagged_spans},
        )
        return response

    # Phase 0: mock answer. Phase 2 replaces this with the LangGraph pipeline.
    response = AgentResponse(
        answer=f"Mock answer for: {redacted_question}",
        status="answered",
        confidence=0.5,
        trace_id=trace_id,
        citations=[
            Citation(
                source_file="packages/contracts/schemas.py",
                text="Phase 0 mock citation.",
                locator=Locator(page=1),
            )
        ],
        flags=flags,
    )
    audit.log_event(trace_id, "ask_answered", {"status": response.status})
    return response
