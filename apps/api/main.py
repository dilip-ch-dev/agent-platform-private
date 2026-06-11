from uuid import uuid4

from fastapi import FastAPI

from packages.agent_core.orchestrator import AgentOrchestrator
from packages.contracts.schemas import AgentRequest, AgentResponse, Citation, Locator
from packages.guardrails.checks import GuardrailChecks
from packages.observability.traces import TraceLogger

app = FastAPI(title="Buildathon Agent Platform", version="0.1.0")
orchestrator = AgentOrchestrator()
guardrails = GuardrailChecks()
trace_logger = TraceLogger()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AgentResponse)
def ask(request: AgentRequest) -> AgentResponse:
    trace_id = str(uuid4())
    trace_logger.log_event(trace_id, "ask_received", {"question": request.question})

    flags = guardrails.validate_input(request)
    if flags:
        response = AgentResponse(
            answer="Request blocked by guardrails.",
            status="blocked",
            confidence=0.0,
            trace_id=trace_id,
            citations=[],
            flags=flags,
        )
        trace_logger.log_event(trace_id, "ask_blocked", {"flags": flags})
        return response

    response = orchestrator.run(request)
    response.trace_id = trace_id
    response.citations = [
        Citation(
            source_file="docs/ARCHITECTURE.md",
            text="Phase 0 mock citation for skeleton validation.",
            locator=Locator(page=1),
        )
    ]
    trace_logger.log_event(trace_id, "ask_answered", {"status": response.status})
    return response
