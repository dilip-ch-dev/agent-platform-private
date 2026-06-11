from packages.contracts.schemas import AgentRequest, AgentResponse


class AgentOrchestrator:
    """Stub LangGraph orchestrator for Phase 0."""

    def run(self, request: AgentRequest) -> AgentResponse:
        return AgentResponse(
            answer=f"Mock answer for: {request.question}",
            status="answered",
            confidence=0.5,
            citations=[],
        )
