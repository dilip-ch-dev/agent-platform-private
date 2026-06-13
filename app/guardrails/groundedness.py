import re

from transformers import pipeline

from app.config import cfg


# Load once at startup
_nli = pipeline(
    "text-classification",
    model="cross-encoder/nli-deberta-v3-base",
)


def split_claims(text: str) -> list[str]:
    """
    Split an answer into individual claims/sentences.
    """
    return [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", text)
        if s.strip()
    ]


def verify_claim(claim: str, evidence: str) -> tuple[str, float]:
    """
    Returns:
        (label, score)

    Labels:
        ENTAILMENT
        NEUTRAL
        CONTRADICTION
    """

    result = _nli(
        {
            "text": evidence,
            "text_pair": claim,
        }
    )

    return result["label"].upper(), result["score"]


def is_grounded(
    claim: str,
    evidence_chunks: list[str],
) -> bool:
    """
    True if ANY evidence chunk supports the claim.
    """

    for evidence in evidence_chunks:
        label, score = verify_claim(
            claim,
            evidence,
        )

        if (
            label == "ENTAILMENT"
            and score >= cfg.groundedness_threshold
        ):
            return True

    return False


def filter_grounded(
    answer: str,
    evidence_chunks: list[str],
) -> tuple[str, float]:
    """
    Returns:
        (filtered_answer, groundedness_score)

    groundedness_score =
        supported_claims / total_claims
    """

    claims = split_claims(answer)

    if not claims:
        return "", 0.0

    supported_claims = [
        claim
        for claim in claims
        if is_grounded(
            claim,
            evidence_chunks,
        )
    ]

    groundedness_score = (
        len(supported_claims)
        / len(claims)
    )

    filtered_answer = " ".join(
        supported_claims
    )

    return (
        filtered_answer,
        round(
            groundedness_score,
            4,
        ),
    )