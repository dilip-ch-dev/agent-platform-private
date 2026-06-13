from app.guardrails.groundedness import (
    filter_grounded,
    split_claims,
)


def test_split_claims():
    claims = split_claims(
        "The sky is blue. Water is wet. Fire is hot."
    )

    assert len(claims) == 3


def test_supported_claim_passes():
    evidence = [
        "LangGraph is a library for building stateful, multi-actor applications with LLMs."
    ]

    answer = (
        "LangGraph helps build stateful LLM applications."
    )

    filtered, score = filter_grounded(
        answer,
        evidence,
    )

    assert score > 0.5
    assert len(filtered) > 0


def test_unsupported_claim_stripped():
    evidence = [
        "The sky is blue."
    ]

    answer = (
        "The ocean is made of chocolate."
    )

    filtered, score = filter_grounded(
        answer,
        evidence,
    )

    assert score == 0.0
    assert filtered == ""   