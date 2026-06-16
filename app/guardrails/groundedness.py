import asyncio
import logging
import re
from functools import lru_cache
from typing import Literal, Mapping, Protocol, TypeAlias

from pydantic import BaseModel, ConfigDict, Field

from app.config import cfg

logger = logging.getLogger(__name__)

MODEL_NAME = "cross-encoder/nli-deberta-v3-base"
VerifierOutput: TypeAlias = Mapping[str, str | float | int]
Label = Literal[
    "ENTAILMENT",
    "NEUTRAL",
    "CONTRADICTION",
    "UNKNOWN",
    "VERIFIER_FAILED",
]
FailureReason = Literal[
    "groundedness verifier failed",
    "groundedness verifier failed for all claims",
    "groundedness verifier failed for one or more claims",
]


class VerifierProtocol(Protocol):
    def __call__(self, text: str, *, text_pair: str) -> list[VerifierOutput]: ...


@lru_cache(maxsize=1)
def _get_nli_verifier(model_id: str) -> VerifierProtocol:
    from transformers import pipeline

    logger.info("Loading groundedness model: %s", model_id)
    return pipeline("text-classification", model=model_id)


_DOT = "__GROUND_DOT__"
_URL_RE = re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE)
_ABBREVIATIONS = (
    "approx.",
    "dr.",
    "mr.",
    "mrs.",
    "ms.",
    "prof.",
    "sr.",
    "jr.",
    "st.",
    "vs.",
    "etc.",
    "e.g.",
    "i.e.",
    "u.s.",
    "u.k.",
)


def _protect_url(match: re.Match[str]) -> str:
    token = match.group(0)
    trailing = ""
    while token and token[-1] in ".!?":
        trailing = token[-1] + trailing
        token = token[:-1]
    return token.replace(".", _DOT) + trailing


def _protect_abbreviation(match: re.Match[str]) -> str:
    return match.group(0).replace(".", _DOT)


def _protect_sentence_punctuation(text: str) -> str:
    protected = _URL_RE.sub(_protect_url, text)
    protected = re.sub(r"(?<=\d)\.(?=\d)", _DOT, protected)

    for abbreviation in _ABBREVIATIONS:
        protected = re.sub(
            re.escape(abbreviation),
            _protect_abbreviation,
            protected,
            flags=re.IGNORECASE,
        )

    return protected


def split_claims(text: str) -> list[str]:
    """
    Split an answer into individual claims/sentences.
    """
    normalized = " ".join(text.strip().split())
    if not normalized:
        return []

    protected = _protect_sentence_punctuation(normalized)
    return [
        sentence.replace(_DOT, ".").strip()
        for sentence in re.split(r"(?<=[.!?])\s+", protected)
        if sentence.replace(_DOT, ".").strip()
    ]


class ClaimVerificationResult(BaseModel):
    model_config = ConfigDict(strict=True)

    claim: str
    label: Label
    score: float = Field(ge=0.0, le=1.0)
    grounded: bool
    failure_reason: FailureReason | None = None


def _normalize_label(raw_label: object) -> Label:
    label = str(raw_label or "UNKNOWN").upper()
    if label == "ENTAILMENT":
        return "ENTAILMENT"
    if label == "NEUTRAL":
        return "NEUTRAL"
    if label == "CONTRADICTION":
        return "CONTRADICTION"
    return "UNKNOWN"


def _normalize_score(raw_score: object) -> float:
    try:
        score = float(raw_score)
    except (TypeError, ValueError):
        return 0.0
    return min(max(score, 0.0), 1.0)


def _first_result(results: list[VerifierOutput]) -> VerifierOutput:
    return results[0] if results else {}


def verify_claim(
    claim: str,
    evidence: str,
    verifier: VerifierProtocol | None = None,
) -> ClaimVerificationResult:
    """
    Returns a single claim verification result for one claim/evidence pair.
    """
    if verifier is None:
        # Use filter_grounded_async from async request handlers.
        verifier = _get_nli_verifier(cfg.groundedness_model)

    try:
        result = _first_result(verifier(evidence, text_pair=claim))

        label = _normalize_label(result.get("label"))
        score = _normalize_score(result.get("score"))
        grounded = label == "ENTAILMENT" and score >= cfg.groundedness_threshold

        return ClaimVerificationResult(
            claim=claim,
            label=label,
            score=score,
            grounded=grounded,
        )
    except Exception as exc:
        logger.warning(
            "Groundedness verification failed; "
            "claim_length=%d evidence_length=%d error_type=%s",
            len(claim),
            len(evidence),
            type(exc).__name__,
        )
        return ClaimVerificationResult(
            claim=claim,
            label="VERIFIER_FAILED",
            score=0.0,
            grounded=False,
            failure_reason="groundedness verifier failed",
        )


def evaluate_claim(
    claim: str,
    evidence_chunks: list[str],
    verifier: VerifierProtocol | None = None,
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
    first_failure: ClaimVerificationResult | None = None

    for position, evidence in enumerate(evidence_chunks, start=1):
        claim_result = verify_claim(claim, evidence, verifier=verifier)

        if claim_result.failure_reason:
            if first_failure is None:
                first_failure = claim_result
            logger.warning("Skipping failed groundedness evidence chunk.")
            continue

        if claim_result.grounded:
            logger.debug(
                "Claim grounded after %d/%d evidence chunks evaluated.",
                position,
                len(evidence_chunks),
            )
            return claim_result

        if best_result is None or claim_result.score > best_result.score:
            best_result = claim_result

    if best_result is not None:
        return best_result

    return first_failure or ClaimVerificationResult(
        claim=claim,
        label="UNKNOWN",
        score=0.0,
        grounded=False,
    )


def is_grounded(
    claim: str,
    evidence_chunks: list[str],
    verifier: VerifierProtocol | None = None,
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
    failure_reason: FailureReason | None = None
    partial: bool = False


def filter_grounded(
    answer: str,
    evidence_chunks: list[str],
    verifier: VerifierProtocol | None = None,
) -> GroundednessResult:
    """
    Returns a typed groundedness result containing the filtered answer,
    the groundedness score, per-claim detail, and any failure reason.

    The score is fail-closed: supported claims divided by total claims. Failed
    verifier calls lower the score while remaining distinguishable via
    ``partial`` and ``failure_reason``.
    """
    claims = split_claims(answer)

    if not claims:
        return GroundednessResult(
            filtered_answer="",
            groundedness_score=0.0,
            claim_results=[],
        )

    claim_results = [
        evaluate_claim(claim, evidence_chunks, verifier=verifier) for claim in claims
    ]

    evaluated_claims = [
        claim_result
        for claim_result in claim_results
        if not claim_result.failure_reason
    ]
    failed_claims = [
        claim_result for claim_result in claim_results if claim_result.failure_reason
    ]

    if failed_claims and not evaluated_claims:
        return GroundednessResult(
            filtered_answer="",
            groundedness_score=0.0,
            claim_results=claim_results,
            failure_reason="groundedness verifier failed for all claims",
        )

    supported_claims = [
        claim_result.claim for claim_result in evaluated_claims if claim_result.grounded
    ]

    filtered_answer = " ".join(supported_claims)
    groundedness_score = (
        round(
            len(supported_claims) / len(claims),
            4,
        )
        if claims
        else 0.0
    )

    return GroundednessResult(
        filtered_answer=filtered_answer,
        groundedness_score=groundedness_score,
        claim_results=claim_results,
        failure_reason=(
            "groundedness verifier failed for one or more claims"
            if failed_claims
            else None
        ),
        partial=bool(failed_claims),
    )


async def filter_grounded_async(
    answer: str,
    evidence_chunks: list[str],
    verifier: VerifierProtocol | None = None,
) -> GroundednessResult:
    """
    Async integration entry point for the blocking local groundedness verifier.
    """
    return await asyncio.to_thread(
        filter_grounded,
        answer,
        evidence_chunks,
        verifier,
    )
