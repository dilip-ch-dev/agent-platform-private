from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from packages.contracts.schemas import Locator

SupportedSourceType = Literal["pdf", "txt", "csv", "unknown"]


def _validate_locator(locator: Locator) -> Locator:
    has_position = (
        locator.page is not None
        or locator.row is not None
        or locator.char_start is not None
    )
    if not has_position:
        raise ValueError("Locator must have at least one of page, row, or char_start")
    if locator.char_end is not None and locator.char_start is None:
        raise ValueError("char_end cannot exist without char_start")
    if (
        locator.char_start is not None
        and locator.char_end is not None
        and locator.char_end < locator.char_start
    ):
        raise ValueError("char_end must be >= char_start")
    return locator


class ExtractedUnit(BaseModel):
    unit_id: str
    source_file: str
    source_type: SupportedSourceType = "unknown"
    text: str
    locator: Locator
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("unit_id", "source_file", "text")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("must be non-empty")
        return value

    @model_validator(mode="after")
    def _validate_locator_field(self) -> "ExtractedUnit":
        _validate_locator(self.locator)
        return self


class Chunk(BaseModel):
    chunk_id: str
    source_file: str
    source_type: SupportedSourceType = "unknown"
    text: str
    locator: Locator
    source_unit_ids: list[str] = Field(default_factory=list)
    token_count: int | None = Field(default=None, ge=0)
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("chunk_id", "source_file", "text")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("must be non-empty")
        return value

    @model_validator(mode="after")
    def _validate_locator_field(self) -> "Chunk":
        _validate_locator(self.locator)
        return self


class StoredChunk(BaseModel):
    chunk_id: str
    source_file: str
    source_type: SupportedSourceType = "unknown"
    text: str
    locator: Locator
    tenant_id: str
    collection: str
    vector_id: str | None = None
    embedding_model: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("chunk_id", "source_file", "text", "tenant_id", "collection")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("must be non-empty")
        return value

    @model_validator(mode="after")
    def _validate_locator_field(self) -> "StoredChunk":
        _validate_locator(self.locator)
        return self


class RetrievalResult(BaseModel):
    chunk: StoredChunk
    score: float = Field(ge=0.0, le=1.0)
    rank: int = Field(ge=1)


class IngestResult(BaseModel):
    source_file: str
    tenant_id: str
    collection: str
    extracted_count: int = Field(ge=0)
    chunk_count: int = Field(ge=0)
    stored_count: int = Field(ge=0)
    skipped_count: int = Field(default=0, ge=0)
    replaced_existing: bool = False
    errors: list[str] = Field(default_factory=list)

    @field_validator("source_file", "tenant_id", "collection")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("must be non-empty")
        return value
