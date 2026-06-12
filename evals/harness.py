"""Eval harness — runs evals/corpus.json against a live API.

Usage:
    uv run python evals/harness.py            # needs the API running (bt-dev)

Scores two behaviours per row:
- expected_blocked  -> response.status == "blocked"
- expected_abstain  -> response.status in {"refused", "low_confidence", "review"}

NOTE (Phase 0): the /ask pipeline returns mock answers, so 'answerable' and
'adversarial' rows are meaningful now; 'unanswerable' rows will only pass once
real retrieval + the refusal gate land (Phase 1-3). The harness reports per-type
accuracy and exits 0 — it becomes a CI gate later (EVAL_GATE_ENABLED, Gate 2).
Replace the generic questions with domain rows once the problem statement drops.
"""

import json
from collections import defaultdict
from pathlib import Path

import httpx

from app.config import cfg

_CORPUS = Path(__file__).parent / "corpus.json"
_ABSTAIN_STATUSES = {"refused", "low_confidence", "review"}


def run() -> dict[str, tuple[int, int]]:
    rows = json.loads(_CORPUS.read_text(encoding="utf-8"))
    results: dict[str, tuple[int, int]] = defaultdict(lambda: (0, 0))

    with httpx.Client(base_url=cfg.api_url, timeout=30.0) as client:
        for row in rows:
            response = client.post("/ask", json={"question": row["question"]})
            response.raise_for_status()
            status = response.json()["status"]

            if row["expected_blocked"]:
                ok = status == "blocked"
            elif row["expected_abstain"]:
                ok = status in _ABSTAIN_STATUSES
            else:
                ok = status == "answered"

            passed, total = results[row["type"]]
            results[row["type"]] = (passed + int(ok), total + 1)
            marker = "PASS" if ok else "FAIL"
            print(f"  [{marker}] {row['id']} ({row['type']}): status={status}")

    return dict(results)


def main() -> None:
    print(f"Running eval corpus against {cfg.api_url} ...")
    results = run()
    print("\n── Per-type accuracy ──")
    for row_type, (passed, total) in sorted(results.items()):
        print(f"  {row_type:14s} {passed}/{total}")
    print("\nPhase 0 expectation: answerable + adversarial pass; unanswerable")
    print("passes only after retrieval + refusal gate land (Phases 1-3).")


if __name__ == "__main__":
    main()
