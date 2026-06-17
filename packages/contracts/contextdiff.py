from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from packages.contracts.schemas import Citation, Locator

CorpusVersion = Literal["A", "B"]
ChangeType = Literal["added", "removed", "modified"]
ValueType = Literal["number", "date"]
ReleaseStatus = Literal["PASS", "REVIEW", "BLOCK"]
AnswerStatus = Literal["answered", "refused", "blocked"]
ReasonCode = Literal[
    "changed_statement",
    "numeric_value_changed",
    "date_value_changed",
    "stale_source_retrieved",
    "citation_invalidated",
    "groundedness_regression",
    "answer_changed",
    "low_confidence",
    "blocked_response",
]
ReviewerDisposition = Literal[
    "confirmed defect",
    "false positive",
    "correct but irrelevant",
    "needs human judgment",
    "insufficient information",
]


class ContextDiffBaseModel(BaseModel):
    model_config = ConfigDict(strict=True)


class SourceUnit(ContextDiffBaseModel):
    unit_id: str
    version: CorpusVersion
    source_file: str
    lineage_id: str
    text: str
    locator: Locator
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("unit_id", "source_file", "lineage_id", "text")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must be non-empty")
        return value


class ValueChange(ContextDiffBaseModel):
    value_type: ValueType
    old_value: str
    new_value: str


class ChangedStatement(ContextDiffBaseModel):
    change_id: str
    change_type: ChangeType
    lineage_id: str
    old_unit: SourceUnit | None = None
    new_unit: SourceUnit | None = None
    value_changes: list[ValueChange] = Field(default_factory=list)
    reason_codes: list[ReasonCode] = Field(default_factory=list)


class EvaluationQuery(ContextDiffBaseModel):
    query_id: str
    question: str
    expected_lineage_ids: list[str] = Field(default_factory=list)
    source: Literal["seeded", "generated"] = "seeded"

    @field_validator("query_id", "question")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must be non-empty")
        return value


class GeneratedProbe(ContextDiffBaseModel):
    probe_id: str
    question: str
    source_change_id: str
    expected_lineage_ids: list[str]


class RetrievalHit(ContextDiffBaseModel):
    source_unit: SourceUnit
    rank: int = Field(ge=1)
    score: float = Field(ge=0.0, le=1.0)
    stale: bool = False


class QueryRun(ContextDiffBaseModel):
    query: EvaluationQuery
    version: CorpusVersion
    answer: str
    status: AnswerStatus
    confidence: float = Field(ge=0.0, le=1.0)
    retrieved: list[RetrievalHit] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    groundedness_score: float = Field(ge=0.0, le=1.0)
    citation_valid: bool


class QueryRegression(ContextDiffBaseModel):
    query: EvaluationQuery
    status: ReleaseStatus
    reason_codes: list[ReasonCode]
    old_source_passage: str
    new_source_passage: str
    old_retrieved_chunks: list[RetrievalHit]
    new_retrieved_chunks: list[RetrievalHit]
    old_answer: str
    new_answer: str
    old_run: QueryRun
    new_run: QueryRun
    recommended_human_review: str
    reviewer_disposition: ReviewerDisposition | None = None
    allowed_dispositions: list[ReviewerDisposition] = Field(
        default_factory=lambda: [
            "confirmed defect",
            "false positive",
            "correct but irrelevant",
            "needs human judgment",
            "insufficient information",
        ]
    )


class ContextDiffSummary(ContextDiffBaseModel):
    changed_statements: int = Field(ge=0)
    affected_queries: int = Field(ge=0)
    generated_probes: int = Field(ge=0)
    pass_count: int = Field(ge=0)
    review_count: int = Field(ge=0)
    block_count: int = Field(ge=0)
    stale_retrievals: int = Field(ge=0)


class ContextDiffRequest(ContextDiffBaseModel):
    corpus_a: list[SourceUnit]
    corpus_b: list[SourceUnit]
    evaluation_set: list[EvaluationQuery]


class ContextDiffReport(ContextDiffBaseModel):
    status: ReleaseStatus
    summary: ContextDiffSummary
    changes: list[ChangedStatement]
    affected_queries: list[EvaluationQuery]
    generated_probes: list[GeneratedProbe]
    regressions: list[QueryRegression]
    html_report: str
