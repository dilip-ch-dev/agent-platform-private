from packages.contracts.schemas import AgentResponse


class EvalAdapter:
    """Stub eval adapter for Phase 0."""

    def score(self, response: AgentResponse) -> dict[str, float]:
        return {"mock_score": 1.0}
