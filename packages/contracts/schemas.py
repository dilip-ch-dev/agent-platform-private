from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class Locator(BaseModel):
    page: int | None = None
    char_start: int | None = None
    char_end: int | None = None
    row: int | None = None


class Citation(BaseModel):
    source_file: str
    text: str
    locator: Locator


class HealthResponse(BaseModel):
    status: str


class AgentRequest(BaseModel):
    model_config = ConfigDict(strict=True)

    question: str
    session_id: str | None = None


class AgentResponse(BaseModel):
    answer: str
    status: Literal["answered", "refused", "blocked", "low_confidence", "review"] = (
        "answered"
    )
    confidence: float = Field(ge=0.0, le=1.0)
    trace_id: str = Field(default_factory=lambda: str(uuid4()))
    citations: list[Citation] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
