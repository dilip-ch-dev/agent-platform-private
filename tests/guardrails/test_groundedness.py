import sys
import types

import pytest
from pydantic import ValidationError

from app.config import Config, cfg
from app.guardrails.groundedness import (
    _get_nli_verifier,
    filter_grounded,
    is_grounded,
    split_claims,
)


def make_mock_verifier(mapping: dict[tuple[str, str], list[dict[str, object]]]):
    def verifier(text: str, *, text_pair: str) -> list[dict[str, object]]:
        key = (text, text_pair)
        if key not in mapping:
            raise KeyError(f"unexpected payload: {key}")
        return mapping[key]

    return verifier


def make_config_values(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "env": "test",
        "debug": False,
        "extraction_model": "claude-haiku-4-5",
        "reasoning_model": "claude-sonnet-4-5",
        "extraction_temperature": 0.2,
        "extraction_max_tokens": 1000,
        "reasoning_temperature": 0.7,
        "reasoning_max_tokens": 2000,
        "retrieval_min_score": 0.35,
        "top_k_retrieval": 3,
        "confidence_threshold": 0.7,
        "injection_threshold": 0.75,
        "groundedness_threshold": 0.6,
        "groundedness_model": "cross-encoder/nli-deberta-v3-base",
        "chroma_path": "./data/chroma",
        "audit_log_path": "./data/audit",
        "api_url": "http://127.0.0.1:8000",
    }
    values.update(overrides)
    return values


def test_split_claims_handles_basic_sentences():
    claims = split_claims("The sky is blue. Water is wet. Fire is hot.")

    assert claims == [
        "The sky is blue.",
        "Water is wet.",
        "Fire is hot.",
    ]


def test_split_claims_handles_abbreviation_decimal_url_and_no_terminal():
    claims = split_claims(
        "Approx. 3.14 is pi. Docs live at https://example.com/a.b?x=1. "
        "Final claim has no terminal punctuation"
    )

    assert claims == [
        "Approx. 3.14 is pi.",
        "Docs live at https://example.com/a.b?x=1.",
        "Final claim has no terminal punctuation",
    ]


def test_supported_claim_passes_with_real_verifier_signature():
    evidence = [
        "LangGraph is a library for building stateful, multi-actor applications with LLMs."
    ]

    answer = "LangGraph helps build stateful LLM applications."
    verifier = make_mock_verifier(
        {
            (
                evidence[0],
                answer,
            ): [{"label": "ENTAILMENT", "score": 0.95}],
        }
    )

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert result.groundedness_score == 1.0
    assert result.filtered_answer == answer
    assert result.claim_results[0].grounded is True
    assert result.failure_reason is None


@pytest.mark.parametrize("label", ["CONTRADICTION", "NEUTRAL", "UNEXPECTED_LABEL"])
def test_non_entailment_labels_do_not_ground(label: str):
    evidence = ["The sky is blue."]
    answer = "The ocean is made of chocolate."

    verifier = make_mock_verifier(
        {
            (evidence[0], answer): [{"label": label, "score": 0.98}],
        }
    )

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert result.groundedness_score == 0.0
    assert result.filtered_answer == ""
    assert result.claim_results[0].grounded is False
    assert result.claim_results[0].label in {"CONTRADICTION", "NEUTRAL", "UNKNOWN"}


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
    assert result.claim_results[0].failure_reason is None


def test_partial_support_preserves_supported_claims():
    evidence = ["A is true."]
    answer = "A is true. B is false."

    verifier = make_mock_verifier(
        {
            (evidence[0], "A is true."): [{"label": "ENTAILMENT", "score": 0.9}],
            (evidence[0], "B is false."): [{"label": "NEUTRAL", "score": 0.5}],
        }
    )

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert result.groundedness_score == 0.5
    assert result.filtered_answer == "A is true."
    assert [r.grounded for r in result.claim_results] == [True, False]


def test_threshold_boundary_is_inclusive(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(cfg, "groundedness_threshold", 0.6)
    evidence = ["The statement is true."]
    answer = "The statement is true."

    verifier = make_mock_verifier(
        {
            (evidence[0], answer): [{"label": "ENTAILMENT", "score": 0.6}],
        }
    )

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert result.groundedness_score == 1.0
    assert result.filtered_answer == answer


def test_threshold_boundary_is_exclusive(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(cfg, "groundedness_threshold", 0.6)
    evidence = ["The statement is true."]
    answer = "The statement is true."

    verifier = make_mock_verifier(
        {
            (evidence[0], answer): [{"label": "ENTAILMENT", "score": 0.599}],
        }
    )

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert result.groundedness_score == 0.0
    assert result.filtered_answer == ""


def test_later_evidence_chunk_can_entail_after_neutral():
    evidence = ["Insufficient context.", "The statement is true."]
    answer = "The statement is true."

    verifier = make_mock_verifier(
        {
            (evidence[0], answer): [{"label": "NEUTRAL", "score": 0.7}],
            (evidence[1], answer): [{"label": "ENTAILMENT", "score": 0.91}],
        }
    )

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert result.groundedness_score == 1.0
    assert result.filtered_answer == answer


def test_first_grounded_chunk_short_circuits():
    evidence = ["The statement is true.", "This should not be checked."]
    answer = "The statement is true."
    calls: list[tuple[str, str]] = []

    def verifier(text: str, *, text_pair: str) -> list[dict[str, object]]:
        calls.append((text, text_pair))
        return [{"label": "ENTAILMENT", "score": 0.91}]

    assert is_grounded(answer, evidence, verifier=verifier) is True
    assert calls == [(evidence[0], answer)]


def test_one_chunk_failure_does_not_stop_later_chunks():
    evidence = ["Broken chunk.", "The statement is true."]
    answer = "The statement is true."
    calls = 0

    def verifier(text: str, *, text_pair: str) -> list[dict[str, object]]:
        nonlocal calls
        calls += 1
        if text == evidence[0]:
            raise RuntimeError("raw evidence failure")
        return [{"label": "ENTAILMENT", "score": 0.91}]

    result = filter_grounded(answer, evidence, verifier=verifier)

    assert calls == 2
    assert result.groundedness_score == 1.0
    assert result.filtered_answer == answer
    assert result.failure_reason is None


def test_partial_claim_failure_is_reviewable_but_usable():
    evidence = ["A is true."]
    answer = "A is true. B cannot be checked. C is not supported."

    def verifier(text: str, *, text_pair: str) -> list[dict[str, object]]:
        if text_pair == "B cannot be checked.":
            raise RuntimeError("raw claim failure")
        if text_pair == "A is true.":
            return [{"label": "ENTAILMENT", "score": 0.9}]
        return [{"label": "NEUTRAL", "score": 0.4}]

    result = filter_grounded(
        answer,
        evidence,
        verifier=verifier,
    )

    assert result.partial is True
    assert (
        result.failure_reason == "groundedness verifier failed for one or more claims"
    )
    assert result.filtered_answer == "A is true."
    assert result.groundedness_score == 0.5
    assert [claim.label for claim in result.claim_results] == [
        "ENTAILMENT",
        "VERIFIER_FAILED",
        "NEUTRAL",
    ]


def test_score_zero_when_all_claims_fail():
    def failing_verifier(text: str, *, text_pair: str) -> list[dict[str, object]]:
        raise RuntimeError("model unavailable with raw details")

    result = filter_grounded(
        "First claim. Second claim.",
        ["Evidence."],
        verifier=failing_verifier,
    )

    assert result.groundedness_score == 0.0
    assert result.filtered_answer == ""
    assert result.partial is False
    assert result.failure_reason == "groundedness verifier failed for all claims"
    assert all(claim.label == "VERIFIER_FAILED" for claim in result.claim_results)


def test_model_failure_logs_sanitized_result(caplog: pytest.LogCaptureFixture):
    def failing_verifier(text: str, *, text_pair: str) -> list[dict[str, object]]:
        raise RuntimeError("secret raw exception")

    with caplog.at_level("WARNING"):
        result = filter_grounded(
            "Secret claim text.",
            ["Secret evidence text."],
            verifier=failing_verifier,
        )

    assert result.claim_results[0].failure_reason == "groundedness verifier failed"
    assert "Secret claim text" not in caplog.text
    assert "Secret evidence text" not in caplog.text
    assert "secret raw exception" not in caplog.text


def test_model_cache_is_keyed_by_model_id(monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple[str, str]] = []

    def pipeline(task: str, *, model: str) -> object:
        calls.append((task, model))
        return object()

    monkeypatch.setitem(
        sys.modules,
        "transformers",
        types.SimpleNamespace(pipeline=pipeline),
    )
    _get_nli_verifier.cache_clear()

    first = _get_nli_verifier("model-a")
    second = _get_nli_verifier("model-a")
    third = _get_nli_verifier("model-b")

    assert first is second
    assert first is not third
    assert calls == [
        ("text-classification", "model-a"),
        ("text-classification", "model-b"),
    ]
    _get_nli_verifier.cache_clear()


def test_groundedness_threshold_is_validated():
    with pytest.raises(ValidationError):
        Config(**make_config_values(groundedness_threshold=1.01))

    with pytest.raises(ValidationError):
        Config(**make_config_values(groundedness_threshold=-0.01))
