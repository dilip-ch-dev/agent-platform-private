from packages.contracts.schemas import AgentRequest


class GuardrailChecks:
    """Stub guardrail checks for Phase 0."""

    def validate_input(self, request: AgentRequest) -> list[str]:
        return []
