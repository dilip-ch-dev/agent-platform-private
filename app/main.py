from uuid import uuid4

from fastapi import FastAPI

from packages.contracts.schemas import (
    AgentRequest,
    AgentResponse,
    Citation,
    HealthResponse,
    Locator,
)

app = FastAPI(title="Buildathon Agent Platform", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/ask", response_model=AgentResponse)
def ask(request: AgentRequest) -> AgentResponse:
    return AgentResponse(
        answer=f"Mock answer for: {request.question}",
        status="answered",
        confidence=0.5,
        trace_id=str(uuid4()),
        citations=[
            Citation(
                source_file="packages/contracts/schemas.py",
                text="Phase 0 mock citation.",
                locator=Locator(page=1),
            )
        ],
    )
