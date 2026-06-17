from __future__ import annotations

import html
import json
import re
from collections.abc import Iterable
from pathlib import Path

from app.config import cfg
from app.guardrails.injection import is_blocked, score
from packages.contracts.contextdiff import (
    ChangedStatement,
    ContextDiffReport,
    ContextDiffRequest,
    ContextDiffSummary,
    EvaluationQuery,
    GeneratedProbe,
    QueryRegression,
    QueryRun,
    ReasonCode,
    ReleaseStatus,
    RetrievalHit,
    SourceUnit,
    ValueChange,
)
from packages.contracts.schemas import Citation

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
_DATE_RE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\s+\d{1,2},\s+\d{4})\b",
    re.IGNORECASE,
)
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "current",
    "does",
    "for",
    "how",
    "is",
    "it",
    "many",
    "of",
    "on",
    "or",
    "policy",
    "say",
    "the",
    "to",
    "what",
    "when",
}


def normalize_statement(text: str) -> str:
    return " ".join(_TOKEN_RE.findall(text.lower()))


def extract_numbers(text: str) -> list[str]:
    return _NUMBER_RE.findall(text)


def extract_dates(text: str) -> list[str]:
    return [match.group(0) for match in _DATE_RE.finditer(text)]


def diff_corpus(
    corpus_a: list[SourceUnit], corpus_b: list[SourceUnit]
) -> list[ChangedStatement]:
    old_by_lineage = {unit.lineage_id: unit for unit in corpus_a}
    new_by_lineage = {unit.lineage_id: unit for unit in corpus_b}
    changes: list[ChangedStatement] = []

    for lineage_id in sorted(old_by_lineage.keys() | new_by_lineage.keys()):
        old_unit = old_by_lineage.get(lineage_id)
        new_unit = new_by_lineage.get(lineage_id)
        if old_unit is None and new_unit is not None:
            changes.append(
                ChangedStatement(
                    change_id=f"chg_{lineage_id}",
                    change_type="added",
                    lineage_id=lineage_id,
                    new_unit=new_unit,
                    reason_codes=["changed_statement"],
                )
            )
            continue
        if new_unit is None and old_unit is not None:
            changes.append(
                ChangedStatement(
                    change_id=f"chg_{lineage_id}",
                    change_type="removed",
                    lineage_id=lineage_id,
                    old_unit=old_unit,
                    reason_codes=["changed_statement"],
                )
            )
            continue
        if old_unit is None or new_unit is None:
            continue
        if normalize_statement(old_unit.text) == normalize_statement(new_unit.text):
            continue

        value_changes = _value_changes(old_unit.text, new_unit.text)
        reason_codes: list[ReasonCode] = ["changed_statement"]
        if any(change.value_type == "number" for change in value_changes):
            reason_codes.append("numeric_value_changed")
        if any(change.value_type == "date" for change in value_changes):
            reason_codes.append("date_value_changed")
        changes.append(
            ChangedStatement(
                change_id=f"chg_{lineage_id}",
                change_type="modified",
                lineage_id=lineage_id,
                old_unit=old_unit,
                new_unit=new_unit,
                value_changes=value_changes,
                reason_codes=reason_codes,
            )
        )

    return changes


def _value_changes(old_text: str, new_text: str) -> list[ValueChange]:
    changes: list[ValueChange] = []
    old_numbers = extract_numbers(old_text)
    new_numbers = extract_numbers(new_text)
    if old_numbers != new_numbers:
        for old_value, new_value in zip(old_numbers, new_numbers, strict=False):
            if old_value != new_value:
                changes.append(
                    ValueChange(
                        value_type="number",
                        old_value=old_value,
                        new_value=new_value,
                    )
                )
        if len(old_numbers) != len(new_numbers):
            changes.append(
                ValueChange(
                    value_type="number",
                    old_value=", ".join(old_numbers),
                    new_value=", ".join(new_numbers),
                )
            )

    old_dates = extract_dates(old_text)
    new_dates = extract_dates(new_text)
    if old_dates != new_dates:
        for old_value, new_value in zip(old_dates, new_dates, strict=False):
            if old_value != new_value:
                changes.append(
                    ValueChange(
                        value_type="date",
                        old_value=old_value,
                        new_value=new_value,
                    )
                )
        if len(old_dates) != len(new_dates):
            changes.append(
                ValueChange(
                    value_type="date",
                    old_value=", ".join(old_dates),
                    new_value=", ".join(new_dates),
                )
            )
    return changes


def retrieve(
    question: str, corpus: list[SourceUnit], top_k: int = 3
) -> list[RetrievalHit]:
    query_tokens = _content_tokens(question)
    if not query_tokens:
        return []

    hits: list[RetrievalHit] = []
    for unit in corpus:
        unit_tokens = _content_tokens(unit.text)
        if not unit_tokens:
            continue
        overlap = query_tokens & unit_tokens
        score_value = len(overlap) / len(query_tokens)
        if score_value <= 0:
            continue
        bias = _retrieval_bias(unit)
        hits.append(
            RetrievalHit(
                source_unit=unit,
                rank=1,
                score=min(round(score_value + bias, 4), 1.0),
                stale=is_stale_unit(unit),
            )
        )

    hits = sorted(
        hits,
        key=lambda hit: (
            -hit.score,
            0 if hit.stale else 1,
            hit.source_unit.source_file,
            hit.source_unit.unit_id,
        ),
    )[:top_k]
    return [
        RetrievalHit(
            source_unit=hit.source_unit,
            rank=index,
            score=hit.score,
            stale=hit.stale,
        )
        for index, hit in enumerate(hits, start=1)
    ]


def _content_tokens(text: str) -> set[str]:
    return {
        token for token in _TOKEN_RE.findall(text.lower()) if token not in _STOPWORDS
    }


def _retrieval_bias(unit: SourceUnit) -> float:
    raw_value = unit.metadata.get("retrieval_bias", "0")
    try:
        return max(min(float(raw_value), 0.05), 0.0)
    except ValueError:
        return 0.0


def is_stale_unit(unit: SourceUnit) -> bool:
    return "stale_of_lineage_id" in unit.metadata or "stale_of_unit_id" in unit.metadata


def map_affected_queries(
    evaluation_set: list[EvaluationQuery],
    changes: list[ChangedStatement],
    corpus_a: list[SourceUnit],
    corpus_b: list[SourceUnit],
) -> list[EvaluationQuery]:
    changed_lineages = {change.lineage_id for change in changes}
    affected: list[EvaluationQuery] = []

    for query in evaluation_set:
        expected_overlap = changed_lineages & set(query.expected_lineage_ids)
        old_overlap = _retrieved_lineage_overlap(
            query.question, corpus_a, changed_lineages
        )
        new_overlap = _retrieved_lineage_overlap(
            query.question, corpus_b, changed_lineages
        )
        if expected_overlap or old_overlap or new_overlap:
            affected.append(query)

    return sorted(affected, key=lambda query: query.query_id)


def _retrieved_lineage_overlap(
    question: str, corpus: list[SourceUnit], changed_lineages: set[str]
) -> set[str]:
    lineages: set[str] = set()
    for hit in retrieve(question, corpus):
        unit = hit.source_unit
        candidate_lineages = {unit.lineage_id}
        stale_lineage = unit.metadata.get("stale_of_lineage_id")
        if stale_lineage:
            candidate_lineages.add(stale_lineage)
        lineages.update(candidate_lineages & changed_lineages)
    return lineages


def generate_probes(changes: list[ChangedStatement]) -> list[GeneratedProbe]:
    probes: list[GeneratedProbe] = []
    for change in sorted(changes, key=lambda item: item.change_id):
        if change.change_type != "modified":
            continue
        combined_text = " ".join(
            unit.text for unit in [change.old_unit, change.new_unit] if unit is not None
        ).lower()
        if "refund" in combined_text and "day" in combined_text:
            questions = [
                "How many days are refunds available after purchase?",
                "What is the current refund window?",
            ]
        else:
            subject = change.lineage_id.replace("_", " ")
            questions = [f"What does the policy say about {subject}?"]

        for index, question in enumerate(questions, start=1):
            probes.append(
                GeneratedProbe(
                    probe_id=f"probe_{change.change_id}_{index}",
                    question=question,
                    source_change_id=change.change_id,
                    expected_lineage_ids=[change.lineage_id],
                )
            )
    return probes


def run_query(
    query: EvaluationQuery,
    version: str,
    corpus: list[SourceUnit],
    current_source_by_lineage: dict[str, SourceUnit],
) -> QueryRun:
    injection_score, _ = score(query.question)
    if is_blocked(injection_score, cfg.injection_threshold, cfg.injection_mode):
        return QueryRun(
            query=query,
            version="A" if version == "A" else "B",
            answer="Request blocked by prompt-injection policy.",
            status="blocked",
            confidence=0.0,
            retrieved=[],
            citations=[],
            groundedness_score=0.0,
            citation_valid=False,
        )

    hits = retrieve(query.question, corpus, top_k=cfg.top_k_retrieval)
    if not hits:
        return QueryRun(
            query=query,
            version="A" if version == "A" else "B",
            answer="I do not have enough cited policy evidence to answer.",
            status="refused",
            confidence=0.0,
            retrieved=[],
            citations=[],
            groundedness_score=0.0,
            citation_valid=False,
        )

    top_hit = hits[0]
    answer = _answer_from_hit(query.question, top_hit.source_unit)
    citation = Citation(
        source_file=top_hit.source_unit.source_file,
        text=top_hit.source_unit.text,
        locator=top_hit.source_unit.locator,
    )
    citation_valid = not top_hit.stale
    expected_sources = [
        current_source_by_lineage[lineage_id]
        for lineage_id in query.expected_lineage_ids
        if lineage_id in current_source_by_lineage
    ]
    groundedness_score = deterministic_groundedness(
        answer, expected_sources or [top_hit.source_unit]
    )

    return QueryRun(
        query=query,
        version="A" if version == "A" else "B",
        answer=answer,
        status="answered",
        confidence=_confidence(top_hit.score, groundedness_score, citation_valid),
        retrieved=hits,
        citations=[citation],
        groundedness_score=groundedness_score,
        citation_valid=citation_valid,
    )


def _answer_from_hit(question: str, unit: SourceUnit) -> str:
    numbers = extract_numbers(unit.text)
    lower_question = question.lower()
    lower_text = unit.text.lower()
    if "refund" in lower_question and "refund" in lower_text and numbers:
        return f"Refunds are available for {numbers[0]} days after purchase."
    if "shipping" in lower_question and numbers:
        return f"Standard shipping takes {numbers[0]} business days."
    if "warranty" in lower_question and numbers:
        return f"Hardware repairs are covered for {numbers[0]} year."
    return unit.text


def deterministic_groundedness(answer: str, evidence_units: list[SourceUnit]) -> float:
    evidence_text = " ".join(unit.text for unit in evidence_units)
    answer_numbers = extract_numbers(answer)
    evidence_numbers = set(extract_numbers(evidence_text))
    if answer_numbers and not set(answer_numbers).issubset(evidence_numbers):
        return 0.0

    answer_tokens = _content_tokens(answer)
    evidence_tokens = _content_tokens(evidence_text)
    if not answer_tokens:
        return 0.0
    overlap = answer_tokens & evidence_tokens
    return 1.0 if len(overlap) / len(answer_tokens) >= 0.5 else 0.0


def _confidence(
    score_value: float, groundedness_score: float, citation_valid: bool
) -> float:
    citation_score = 1.0 if citation_valid else 0.0
    return round(
        min(0.5 * groundedness_score + 0.3 * score_value + 0.2 * citation_score, 1.0),
        4,
    )


def classify_regression(
    query: EvaluationQuery,
    changes: list[ChangedStatement],
    old_run: QueryRun,
    new_run: QueryRun,
) -> QueryRegression:
    change = _primary_change(query, changes, old_run, new_run)
    old_source = change.old_unit.text if change and change.old_unit else ""
    new_source = change.new_unit.text if change and change.new_unit else ""
    reason_codes: list[ReasonCode] = []

    if new_run.status == "blocked":
        reason_codes.append("blocked_response")
    if any(hit.stale for hit in new_run.retrieved):
        reason_codes.append("stale_source_retrieved")
    if not new_run.citation_valid:
        reason_codes.append("citation_invalidated")
    if old_run.groundedness_score > new_run.groundedness_score:
        reason_codes.append("groundedness_regression")
    if old_run.answer != new_run.answer:
        reason_codes.append("answer_changed")
    if new_run.confidence < cfg.confidence_threshold:
        reason_codes.append("low_confidence")

    reason_codes = _dedupe_reason_codes(reason_codes)
    status = _release_status(reason_codes)
    return QueryRegression(
        query=query,
        status=status,
        reason_codes=reason_codes,
        old_source_passage=old_source,
        new_source_passage=new_source,
        old_retrieved_chunks=old_run.retrieved,
        new_retrieved_chunks=new_run.retrieved,
        old_answer=old_run.answer,
        new_answer=new_run.answer,
        old_run=old_run,
        new_run=new_run,
        recommended_human_review=_review_recommendation(status, reason_codes),
    )


def _primary_change(
    query: EvaluationQuery,
    changes: list[ChangedStatement],
    old_run: QueryRun,
    new_run: QueryRun,
) -> ChangedStatement | None:
    expected = set(query.expected_lineage_ids)
    for change in changes:
        if change.lineage_id in expected:
            return change
    retrieved_lineages = {
        lineage
        for run in [old_run, new_run]
        for hit in run.retrieved
        for lineage in _hit_lineages(hit)
    }
    for change in changes:
        if change.lineage_id in retrieved_lineages:
            return change
    return changes[0] if changes else None


def _hit_lineages(hit: RetrievalHit) -> set[str]:
    lineages = {hit.source_unit.lineage_id}
    stale_lineage = hit.source_unit.metadata.get("stale_of_lineage_id")
    if stale_lineage:
        lineages.add(stale_lineage)
    return lineages


def _dedupe_reason_codes(reason_codes: Iterable[ReasonCode]) -> list[ReasonCode]:
    seen: set[ReasonCode] = set()
    deduped: list[ReasonCode] = []
    for reason_code in reason_codes:
        if reason_code not in seen:
            seen.add(reason_code)
            deduped.append(reason_code)
    return deduped


def _release_status(reason_codes: list[ReasonCode]) -> ReleaseStatus:
    block_reasons = {
        "blocked_response",
        "citation_invalidated",
        "groundedness_regression",
        "stale_source_retrieved",
    }
    if block_reasons & set(reason_codes):
        return "BLOCK"
    review_reasons = {"answer_changed", "low_confidence"}
    if review_reasons & set(reason_codes):
        return "REVIEW"
    return "PASS"


def _review_recommendation(
    status: ReleaseStatus, reason_codes: list[ReasonCode]
) -> str:
    if status == "BLOCK":
        return (
            "Block release until stale retrieval and citation grounding are repaired; "
            f"machine reasons: {', '.join(reason_codes)}."
        )
    if status == "REVIEW":
        return (
            "Ask a reviewer to confirm whether the changed answer is expected; "
            f"machine reasons: {', '.join(reason_codes)}."
        )
    return "No human review required for this query."


def run_contextdiff(request: ContextDiffRequest) -> ContextDiffReport:
    changes = diff_corpus(request.corpus_a, request.corpus_b)
    affected_queries = map_affected_queries(
        request.evaluation_set,
        changes,
        request.corpus_a,
        request.corpus_b,
    )
    probes = generate_probes(changes)
    generated_queries = [
        EvaluationQuery(
            query_id=probe.probe_id,
            question=probe.question,
            expected_lineage_ids=probe.expected_lineage_ids,
            source="generated",
        )
        for probe in probes
    ]
    query_plan = affected_queries + generated_queries
    old_sources = {unit.lineage_id: unit for unit in request.corpus_a}
    new_sources = {
        unit.lineage_id: unit for unit in request.corpus_b if not is_stale_unit(unit)
    }

    regressions = [
        classify_regression(
            query=query,
            changes=changes,
            old_run=run_query(query, "A", request.corpus_a, old_sources),
            new_run=run_query(query, "B", request.corpus_b, new_sources),
        )
        for query in query_plan
    ]
    status = _overall_status(regressions)
    summary = ContextDiffSummary(
        changed_statements=len(changes),
        affected_queries=len(affected_queries),
        generated_probes=len(probes),
        pass_count=sum(1 for item in regressions if item.status == "PASS"),
        review_count=sum(1 for item in regressions if item.status == "REVIEW"),
        block_count=sum(1 for item in regressions if item.status == "BLOCK"),
        stale_retrievals=sum(
            1 for item in regressions for hit in item.new_retrieved_chunks if hit.stale
        ),
    )
    report_without_html = ContextDiffReport(
        status=status,
        summary=summary,
        changes=changes,
        affected_queries=affected_queries,
        generated_probes=probes,
        regressions=regressions,
        html_report="",
    )
    return report_without_html.model_copy(
        update={"html_report": render_html_report(report_without_html)}
    )


def _overall_status(regressions: list[QueryRegression]) -> ReleaseStatus:
    if any(regression.status == "BLOCK" for regression in regressions):
        return "BLOCK"
    if any(regression.status == "REVIEW" for regression in regressions):
        return "REVIEW"
    return "PASS"


def render_html_report(report: ContextDiffReport) -> str:
    rows = []
    for regression in report.regressions:
        row_class = regression.status.lower()
        rows.append(
            "<tr>"
            f"<td>{html.escape(regression.status)}</td>"
            f"<td>{html.escape(regression.query.query_id)}</td>"
            f"<td>{html.escape(regression.query.question)}</td>"
            f"<td>{html.escape(', '.join(regression.reason_codes) or 'none')}</td>"
            f"<td>{html.escape(regression.old_answer)}</td>"
            f"<td>{html.escape(regression.new_answer)}</td>"
            f"<td>{html.escape(regression.recommended_human_review)}</td>"
            "</tr>".replace("<tr>", f'<tr class="{row_class}">')
        )
    changes = "".join(
        "<li>"
        f"{html.escape(change.change_type.upper())}: "
        f"{html.escape(change.old_unit.text if change.old_unit else '')} "
        f"&rarr; {html.escape(change.new_unit.text if change.new_unit else '')}"
        "</li>"
        for change in report.changes
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ContextDiff Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #202124; }}
    h1 {{ margin-bottom: 4px; }}
    .status {{ font-size: 24px; font-weight: 700; }}
    .BLOCK {{ color: #b3261e; }}
    .REVIEW {{ color: #9a6700; }}
    .PASS {{ color: #137333; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 18px; }}
    th, td {{ border: 1px solid #dadce0; padding: 8px; vertical-align: top; }}
    th {{ background: #f1f3f4; text-align: left; }}
    tr.block {{ background: #fce8e6; }}
    tr.review {{ background: #fef7e0; }}
    tr.pass {{ background: #e6f4ea; }}
    code {{ background: #f1f3f4; padding: 2px 4px; }}
  </style>
</head>
<body>
  <h1>ContextDiff Release Gate</h1>
  <div class="status {report.status}">Release status: {report.status}</div>
  <p>
    Changed policy detected: {report.summary.changed_statements};
    affected queries identified: {report.summary.affected_queries};
    stale source retrieved: {report.summary.stale_retrievals}.
  </p>
  <h2>Changed Statements</h2>
  <ul>{changes}</ul>
  <h2>Regressions</h2>
  <table>
    <thead>
      <tr>
        <th>Status</th><th>Query</th><th>Question</th><th>Reasons</th>
        <th>Old answer</th><th>New answer</th><th>Review</th>
      </tr>
    </thead>
    <tbody>{"".join(rows)}</tbody>
  </table>
</body>
</html>"""


def write_report(report: ContextDiffReport, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "contextdiff_report.json"
    html_path = output_dir / "contextdiff_report.html"
    json_path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    html_path.write_text(report.html_report, encoding="utf-8")
    return json_path, html_path


def load_request_from_json(path: Path) -> ContextDiffRequest:
    return ContextDiffRequest.model_validate(
        json.loads(path.read_text(encoding="utf-8"))
    )
