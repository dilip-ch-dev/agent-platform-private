import re
from functools import lru_cache
from typing import Callable, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.config import cfg

MODEL_NAME = "cross-encoder/nli-deberta-v3-base"
Verifier = Callable[[dict[str, str]], dict[str, object]]


@lru_cache(maxsize=1)
def _get_nli_verifier() -> object:
    from transformers import pipeline

    model_id = cfg.groundedness_model or MODEL_NAME
    return pipeline("text-classification", model=model_id)


def split_claims(text: str) -> list[str]:
    """
    Split an answer into individual claims/sentences.
    """
    return [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", text)
        if s.strip()
    ]


class ClaimVerificationResult(BaseModel):
    model_config = ConfigDict(strict=True)

    claim: str
    label: Literal["ENTAILMENT", "NEUTRAL", "CONTRADICTION", "UNKNOWN"]
    score: float = Field(ge=0.0, le=1.0)
    grounded: bool
    failure_reason: str | None = None


def verify_claim(
    claim: str,
    evidence: str,
    verifier: Verifier | None = None,
) -> ClaimVerificationResult:
    """
    Returns a single claim verification result for one claim/evidence pair.
    """
    if verifier is None:
        verifier = _get_nli_verifier()

    try:
        result = verifier(
            {
                "text": evidence,
                "text_pair": claim,
            }
        )

        label = str(result.get("label", "UNKNOWN")).upper()
        score = float(result.get("score", 0.0))

        if label not in {"ENTAILMENT", "NEUTRAL", "CONTRADICTION"}:
            label = "UNKNOWN"

        grounded = (
            label == "ENTAILMENT"
            and score >= cfg.groundedness_threshold
        )

        return ClaimVerificationResult(
            claim=claim,
            label=label,
            score=score,
            grounded=grounded,
        )
    except Exception as exc:
        return ClaimVerificationResult(
            claim=claim,
            label="UNKNOWN",
            score=0.0,
            grounded=False,
            failure_reason=f"groundedness verifier failed: {exc}",
        )


def evaluate_claim(
    claim: str,
    evidence_chunks: list[str],
    verifier: Verifier | None = None,
) -> ClaimVerificationResult:
    """
    Returns the best verification result for a claim across evidence chunks.
    """
    if not evidence_chunks:
        return ClaimVerificationResult(
            claim=claim,
            label="UNKNOWN",
            score=0.0,
            grounded=False,
        )

    best_result: ClaimVerificationResult | None = None

    for evidence in evidence_chunks:
        claim_result = verify_claim(claim, evidence, verifier=verifier)

        if claim_result.failure_reason:
            return claim_result

        if claim_result.grounded:
            return claim_result

        if best_result is None or claim_result.score > best_result.score:
            best_result = claim_result

    return best_result or ClaimVerificationResult(
        claim=claim,
        label="UNKNOWN",
        score=0.0,
        grounded=False,
    )


def is_grounded(
    claim: str,
    evidence_chunks: list[str],
    verifier: Verifier | None = None,
) -> bool:
    """
    True if ANY evidence chunk supports the claim.
    """
    return evaluate_claim(
        claim,
        evidence_chunks,
        verifier=verifier,
    ).grounded


class GroundednessResult(BaseModel):
    model_config = ConfigDict(strict=True)

    filtered_answer: str
    groundedness_score: float = Field(ge=0.0, le=1.0)
    claim_results: list[ClaimVerificationResult]
    failure_reason: str | None = None


def filter_grounded(
    answer: str,
    evidence_chunks: list[str],
    verifier: Verifier | None = None,
) -> GroundednessResult:
    """
    Returns a typed groundedness result containing the filtered answer,
    the groundedness score, per-claim detail, and any failure reason.
    """
    claims = split_claims(answer)

    if not claims:
        return GroundednessResult(
            filtered_answer="",
            groundedness_score=0.0,
            claim_results=[],
        )

    claim_results = [
        evaluate_claim(claim, evidence_chunks, verifier=verifier)
        for claim in claims
    ]

    for claim_result in claim_results:
        if claim_result.failure_reason:
            return GroundednessResult(
                filtered_answer="",
                groundedness_score=0.0,
                claim_results=claim_results,
                failure_reason=claim_result.failure_reason,
            )

    supported_claims = [
        claim_result.claim
        for claim_result in claim_results
        if claim_result.grounded
    ]

    filtered_answer = " ".join(supported_claims)
    groundedness_score = round(
        len(supported_claims) / len(claims),
        4,
    )

    return GroundednessResult(
        filtered_answer=filtered_answer,
        groundedness_score=groundedness_score,
        claim_results=claim_results,
    )
