from packages.contracts.schemas import Citation


class RetrievalPipeline:
    """Stub retrieval pipeline for Phase 0."""

    def search(self, query: str, top_k: int = 5) -> list[Citation]:
        return []
