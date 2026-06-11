from typing import Any, Callable


class ToolRegistry:
    """Stub tool registry for Phase 0."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, handler: Callable[..., Any]) -> None:
        self._tools[name] = handler

    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())
