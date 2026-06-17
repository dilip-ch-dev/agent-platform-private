from __future__ import annotations

from fastapi.testclient import TestClient

from app.contextdiff.demo import load_seed_demo
from app.contextdiff.service import (
    classify_regression,
    deterministic_groundedness,
    diff_corpus,
    generate_probes,
    map_affected_queries,
    retrieve,
    run_contextdiff,
    run_query,
)
from app.main import app
from packages.contracts.contextdiff import (
    ContextDiffReport,
    ContextDiffRequest,
    EvaluationQuery,
    QueryRegression,
    SourceUnit,
)
from packages.contracts.schemas import Locator


def make_unit(
    unit_id: str,
    version: str,
    lineage_id: str,
    text: str,
    metadata: dict[str, str] | None = None,
) -> SourceUnit:
    return SourceUnit(
        unit_id=unit_id,
        version="A" if version == "A" else "B",
        source_file=f"{version}/{lineage_id}.md",
        lineage_id=lineage_id,
        text=text,
        locator=Locator(page=1),
        metadata=metadata or {},
    )


def test_added_removed_and_modified_statement_detection() -> None:
    old_units = [
        make_unit("old_refund", "A", "refund_window", "Refunds last 30 days."),
        make_unit("old_removed", "A", "removed_rule", "Removed text."),
    ]
    new_units = [
        make_unit("new_refund", "B", "refund_window", "Refunds last 14 days."),
        make_unit("new_added", "B", "added_rule", "Added text."),
    ]

    changes = diff_corpus(old_units, new_units)

    assert [change.change_type for change in changes] == [
        "added",
        "modified",
        "removed",
    ]
    modified = next(change for change in changes if change.change_type == "modified")
    assert "numeric_value_changed" in modified.reason_codes
    assert modified.value_changes[0].old_value == "30"
    assert modified.value_changes[0].new_value == "14"


def test_date_change_detection() -> None:
    old_units = [
        make_unit("old_holiday", "A", "holiday", "Exchanges end January 30, 2027.")
    ]
    new_units = [
        make_unit("new_holiday", "B", "holiday", "Exchanges end January 15, 2027.")
    ]

    changes = diff_corpus(old_units, new_units)

    assert any(change.value_type == "date" for change in changes[0].value_changes)
    assert "date_value_changed" in changes[0].reason_codes


def test_stale_content_retrieval_is_detectable() -> None:
    request = load_seed_demo()

    hits = retrieve(
        "How many days are refunds available after purchase?",
        request.corpus_b,
    )

    assert hits[0].stale is True
    assert hits[0].source_unit.metadata["stale_of_lineage_id"] == "refund_window"


def test_change_to_query_mapping_and_unaffected_exclusion() -> None:
    request = load_seed_demo()
    changes = diff_corpus(request.corpus_a, request.corpus_b)

    affected = map_affected_queries(
        request.evaluation_set,
        changes,
        request.corpus_a,
        request.corpus_b,
    )

    affected_ids = {query.query_id for query in affected}
    assert {"q_refund_window", "q_refund_after_two_weeks"} <= affected_ids
    assert "q_shipping_speed" not in affected_ids
    assert "q_warranty_period" not in affected_ids


def test_generated_probes_are_deterministic() -> None:
    request = load_seed_demo()
    changes = diff_corpus(request.corpus_a, request.corpus_b)

    first = generate_probes(changes)
    second = generate_probes(changes)

    assert first == second
    assert [probe.question for probe in first] == [
        "How many days are refunds available after purchase?",
        "What is the current refund window?",
    ]


def test_citation_invalidation_and_groundedness_regression() -> None:
    request = load_seed_demo()
    report = run_contextdiff(request)

    refund_regression = next(
        item for item in report.regressions if item.query.query_id == "q_refund_window"
    )

    assert refund_regression.status == "BLOCK"
    assert "citation_invalidated" in refund_regression.reason_codes
    assert "groundedness_regression" in refund_regression.reason_codes
    assert (
        refund_regression.old_answer
        == "Refunds are available for 30 days after purchase."
    )
    assert (
        refund_regression.new_answer
        == "Refunds are available for 30 days after purchase."
    )
    assert refund_regression.new_source_passage.endswith("14 days after purchase.")


def test_deterministic_groundedness_rejects_old_value_against_new_source() -> None:
    new_source = make_unit(
        "new_refund",
        "B",
        "refund_window",
        "Refunds are available for 14 days after purchase.",
    )

    assert (
        deterministic_groundedness(
            "Refunds are available for 30 days after purchase.",
            [new_source],
        )
        == 0.0
    )


def test_pass_review_and_block_statuses() -> None:
    request = load_seed_demo()
    report = run_contextdiff(request)

    assert report.status == "BLOCK"
    assert any(item.status == "REVIEW" for item in report.regressions)

    unchanged = ContextDiffRequest(
        corpus_a=request.corpus_a,
        corpus_b=[
            unit.model_copy(update={"version": "B"}) for unit in request.corpus_a
        ],
        evaluation_set=request.evaluation_set,
    )
    pass_report = run_contextdiff(unchanged)
    assert pass_report.status == "PASS"


def test_human_dispositions_are_exposed() -> None:
    report = run_contextdiff(load_seed_demo())
    regression = report.regressions[0]

    assert regression.reviewer_disposition is None
    assert regression.allowed_dispositions == [
        "confirmed defect",
        "false positive",
        "correct but irrelevant",
        "needs human judgment",
        "insufficient information",
    ]


def test_json_report_schema_round_trips() -> None:
    report = run_contextdiff(load_seed_demo())

    parsed = ContextDiffReport.model_validate_json(report.model_dump_json())

    assert parsed.status == "BLOCK"
    assert parsed.summary.stale_retrievals >= 1
    assert "Release status: BLOCK" in parsed.html_report


def test_api_level_contextdiff_demo() -> None:
    client = TestClient(app)

    response = client.get("/contextdiff/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "BLOCK"
    assert payload["summary"]["affected_queries"] == 2


def test_classify_regression_can_pass_with_valid_citation() -> None:
    old_unit = make_unit(
        "old", "A", "shipping_speed", "Standard shipping takes 5 days."
    )
    new_unit = make_unit(
        "new", "B", "shipping_speed", "Standard shipping takes 5 days."
    )
    query = EvaluationQuery(
        query_id="q_shipping",
        question="How long does standard shipping take?",
        expected_lineage_ids=["shipping_speed"],
    )
    old_run = run_query(query, "A", [old_unit], {"shipping_speed": old_unit})
    new_run = run_query(query, "B", [new_unit], {"shipping_speed": new_unit})

    regression = classify_regression(query, [], old_run, new_run)

    assert isinstance(regression, QueryRegression)
    assert regression.status == "PASS"
