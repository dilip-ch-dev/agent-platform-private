from app.guardrails.groundedness import (
    GroundednessResult,
    ClaimVerificationResult,
    filter_grounded,
    split_claims,
)


def make_mock_verifier(mapping: dict[tuple[str, str], dict[str, object]]):
    def verifier(payload: dict[str, str]) -> dict[str, object]:
        key = (payload["text"], payload["text_pair"])
        if key not in mapping:
            raise KeyError(f"unexpected payload: {key}")
        return mapping[key]

    return verifier


def test_split_claims():
    claims = split_claims(
        "The sky is blue. Water is wet. Fire is hot."
    )

    assert len(claims) == 3


def test_supported_claim_passes():
    evidence = [
        "LangGraph is a library for building stateful, multi-actor applications with LLMs."
    ]

    answer = "LangGraph helps build stateful LLM applications."
    verifier = make_mock_verifier({
        (
            evidence[0],
            answer,
        ): {"label": "ENTAILMENT", "score": 0.95},
    })

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert isinstance(result, GroundednessResult)
    assert result.groundedness_score == 1.0
    assert result.filtered_answer == answer
    assert result.claim_results[0].grounded is True
    assert result.failure_reason is None


def test_unsupported_claim_stripped():
    evidence = ["The sky is blue."]
    answer = "The ocean is made of chocolate."

    verifier = make_mock_verifier({
        (evidence[0], answer): {"label": "CONTRADICTION", "score": 0.98},
    })

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert result.groundedness_score == 0.0
    assert result.filtered_answer == ""
    assert result.claim_results[0].grounded is False
    assert result.claim_results[0].label == "CONTRADICTION"


def test_empty_answer_returns_empty_result():
    result = filter_grounded("", ["some evidence"], verifier=make_mock_verifier({}))

    assert result.groundedness_score == 0.0
    assert result.filtered_answer == ""
    assert result.claim_results == []
    assert result.failure_reason is None


def test_empty_evidence_results_in_unknown_claim():
    answer = "Nothing in the evidence supports this."
    result = filter_grounded(answer, [], verifier=make_mock_verifier({}))

    assert result.groundedness_score == 0.0
    assert result.filtered_answer == ""
    assert len(result.claim_results) == 1
    assert result.claim_results[0].label == "UNKNOWN"
    assert result.claim_results[0].grounded is False


def test_partial_support_preserves_supported_claims():
    evidence = ["A is true."]
    answer = "A is true. B is false."

    verifier = make_mock_verifier({
        (evidence[0], "A is true."): {"label": "ENTAILMENT", "score": 0.9},
        (evidence[0], "B is false."): {"label": "NEUTRAL", "score": 0.5},
    })

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert result.groundedness_score == 0.5
    assert result.filtered_answer == "A is true."
    assert [r.grounded for r in result.claim_results] == [True, False]


def test_neutral_result_does_not_ground():
    evidence = ["The fact is unknown."]
    answer = "The fact is unknown."

    verifier = make_mock_verifier({
        (evidence[0], answer): {"label": "NEUTRAL", "score": 0.99},
    })

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert result.groundedness_score == 0.0
    assert result.filtered_answer == ""
    assert result.claim_results[0].label == "NEUTRAL"


def test_contradiction_result_does_not_ground():
    evidence = ["The sky is green."]
    answer = "The sky is blue."

    verifier = make_mock_verifier({
        (evidence[0], answer): {"label": "CONTRADICTION", "score": 0.9},
    })

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert result.groundedness_score == 0.0
    assert result.filtered_answer == ""
    assert result.claim_results[0].label == "CONTRADICTION"


def test_threshold_boundary_is_inclusive():
    from app.config import cfg

    old_threshold = cfg.groundedness_threshold
    cfg.groundedness_threshold = 0.6

    evidence = ["The statement is true."]
    answer = "The statement is true."

    verifier = make_mock_verifier({
        (evidence[0], answer): {"label": "ENTAILMENT", "score": 0.6},
    })

    result = filter_grounded(answer, evidence, verifier=verifier)

    cfg.groundedness_threshold = old_threshold

    assert result.groundedness_score == 1.0
    assert result.filtered_answer == answer


def test_model_failure_returns_reviewable_result():
    def failing_verifier(_: dict[str, str]) -> dict[str, object]:
        raise RuntimeError("model unavailable")

    result = filter_grounded(
        "A claim.",
        ["Evidence."],
        verifier=failing_verifier,
    )

    assert result.groundedness_score == 0.0
    assert result.filtered_answer == ""
    assert result.failure_reason is not None
    assert "groundedness verifier failed" in result.failure_reason
