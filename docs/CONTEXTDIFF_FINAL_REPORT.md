# ContextDiff Final Report

## Workspace

- Workspace path: `D:\ContextDiff`
- Current branch: `personal/contextdiff`
- Validated implementation checkpoint: `391de27a9c035959a5e5fc075bc64091b02e73d3`

## Remotes

- Personal remote `origin`: `https://github.com/dilip-ch-dev/agent-platform-private.git`
- Organization remote `upstream`: `https://github.com/buildathon-labs/agent-platform.git`
- Organization push URL: `DISABLED_NO_PUSH`

No organization repository write operations were performed.

## Starting Point

- Personal `origin/development` at inspection: `8fa869aaab4f6bed111b3b9d2a61a2f2906ff5ce`
- Live organization `upstream/development` base: `31de9c3cfe95835ba4ac036dad52bab0811c0543`
- Implementation branch was created from `upstream/development`.

## PR Branches Inspected

- PR #7 `feature/rag-extraction-chunking-a`
  - Head: `1baf873c1314dbf12ef72caec32e71cadcb8a364`
  - Merge base: `8fa869aaab4f6bed111b3b9d2a61a2f2906ff5ce`
  - Ahead/behind vs live `upstream/development`: `3 behind`, `4 ahead`
  - CI observed via GitHub connector: `CI` completed successfully for run `27641563811`
  - Decision: import the reviewed feature commits instead of merging the branch wholesale because it was based on an older development SHA.

- PR #8 `feature/srivathsav-guardrails`
  - Head: `88e4bfa02c7df27f8ae5bc90c612aa16d8bc6c74`
  - Merge base: `31de9c3cfe95835ba4ac036dad52bab0811c0543`
  - Ahead/behind vs live `upstream/development`: `0 behind`, `5 ahead`
  - CI observed via GitHub connector: `CI` completed successfully for run `27599793259`
  - Decision: import the non-merge feature and repair commits; skip the branch merge commit.

- PR #9 `feature/guardrails-pii-injection`
  - Head: `3747471248a6bff921e879326945c4eabc1dd39a`
  - Merge base: `31de9c3cfe95835ba4ac036dad52bab0811c0543`
  - Ahead/behind vs live `upstream/development`: `0 behind`, `3 ahead`
  - CI observed via GitHub connector: `CI` completed successfully for run `27600874558`
  - Decision: import the reviewed feature and repair commits.

## Commits Imported

PR #7:

- `1bde904` `feat(rag): implement extraction and chunking pipeline`
- `31326b2` `refactor(rag): address PR review feedback for chunking and ingest`
- `370e63e` `chore(format): apply ruff formatting for lint-smoke`
- `1baf873` `chore(lint): remove unused TxtExtractor import in rag tests`

PR #8:

- `4a90733` `Implement NLI groundedness and faithfulness guardrail`
- `ff66b3c` `groundness new changes`
- `dbffbc8` `Repair groundedness review findings`
- `88e4bfa` `Address groundedness follow-up review feedback`
- Skipped `eeadb59` because it was a merge commit from development, not feature content.

PR #9:

- `1742ca6` `Add PII and injection guardrails`
- `f3376ac` `Address PII and injection review feedback`
- `3747471` `Align injection review follow-up details`

## Merge Conflicts and Resolutions

- `.env.example`: resolved adjacent groundedness model and injection mode settings by keeping both.
- `app/config.py`: resolved threshold/model/mode conflicts by keeping groundedness threshold validation, groundedness model configuration, injection threshold validation, and typed injection mode.

## Files Created

- `app/contextdiff/__init__.py`
- `app/contextdiff/demo.py`
- `app/contextdiff/service.py`
- `eval/contextdiff_seed.json`
- `packages/contracts/contextdiff.py`
- `scripts/contextdiff_demo.py`
- `tests/contextdiff/__init__.py`
- `tests/contextdiff/test_contextdiff.py`

## Files Modified

- `.env.example`
- `README.md`
- `app/config.py`
- `app/guardrails/groundedness.py`
- `app/guardrails/injection.py`
- `app/guardrails/pii.py`
- `app/main.py`
- `app/rag/chunker.py`
- `app/rag/ingest.py`
- `packages/contracts/__init__.py`
- `scripts/smoke.py`
- `tests/guardrails/test_groundedness.py`
- `tests/guardrails/test_injection.py`
- `tests/guardrails/test_pii.py`
- `tests/rag/test_ingest.py`
- `tests/test_config.py`
- `ui/app.py`

No files were deleted.

## Architecture Implemented

- Strict Pydantic ContextDiff contracts for source units, changed statements, value changes, evaluation queries, generated probes, retrieval hits, query runs, regressions, summary, request, and report.
- Deterministic corpus differ for added, removed, and modified statements, including numeric and date value changes.
- Deterministic lexical retrieval with stale-source metadata detection.
- Query impact mapping from changed source lineage plus retrieval overlap.
- Deterministic generated probes for changed refund statements.
- Before/after query execution over corpus A and corpus B through the same retrieval and answer path.
- Citation validity, stale retrieval, answer change, confidence, block behavior, and deterministic groundedness comparison.
- Release gate emitting `PASS`, `REVIEW`, or `BLOCK`.
- JSON report and readable HTML report generation.
- Reviewer disposition contract for `confirmed defect`, `false positive`, `correct but irrelevant`, `needs human judgment`, and `insufficient information`.
- FastAPI endpoints:
  - `POST /contextdiff/run`
  - `GET /contextdiff/demo`
- Gradio demo surface for the canonical seeded run.
- Export script writing JSON and HTML reports under ignored `data/audit/contextdiff_demo/`.

## Canonical Demo Result

Seeded corpus:

- Version A says refunds are available for `30 days`.
- Version B changes refunds to `14 days`.
- Version B also contains a stale legacy cache passage with the old `30 days` content.

Observed demo output:

- Changed policy detected: `3`
- Affected seeded queries identified: `2`
- Generated probes: `2`
- Stale source retrieved: `3`
- Release status: `BLOCK`

The report visibly includes the old answer versus new answer, stale retrieval evidence, citation or groundedness regressions, machine-readable reason codes, and recommended human review.

## Validation Results

Passed:

- `uv sync --frozen --extra dev`
- `uv sync --frozen --extra dev --extra pipeline`
- `uv run ruff format --check .`
- `uv run ruff check .`
- `uv run pytest`
  - `149 passed`
- `uv run pytest --cov=app --cov=packages --cov-fail-under=80 --cov-report=term-missing`
  - `149 passed`
  - total coverage: `94.91%`
- `uv run python scripts/smoke.py`
- `uv run python scripts/contextdiff_demo.py`
- `git diff --check`

Warnings:

- FastAPI/Starlette test client emitted a deprecation warning about `httpx`; it does not fail the suite.
- Git on Windows reports line-ending normalization warnings for several text files.

## Run Instructions

Install dependencies:

```powershell
uv sync --frozen --extra dev --extra pipeline
```

Run the API:

```powershell
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run the canonical API demo:

```powershell
curl http://127.0.0.1:8000/contextdiff/demo
```

Export JSON and HTML reports:

```powershell
uv run python scripts/contextdiff_demo.py
```

Run the UI:

```powershell
uv run ui
```

## Credentials

No credentials are required for the deterministic ContextDiff demo, tests, report export, or smoke validation.

The broader agent-platform skeleton still has optional provider keys in `.env.example`, but ContextDiff validation does not require paid APIs or model downloads.

## Deviations

- `CONTEXTDIFF_BUILD_CONTRACT_2026-06-17.md` was not present in the checkout, personal mirror, or Downloads. The available `ContextDiff Implementation Guide.docx` was used as the product contract.
- `gh` is not installed in this environment, so GitHub PR and CI inspection used the GitHub connector plus local `git`.
- The personal repository `dilip-ch-dev/agent-platform-private` already existed, so it was used rather than creating a duplicate repository.
- No push was performed because the guide says to stop and ask for approval before the first push to the public personal repository.
- The MVP uses deterministic lexical retrieval and deterministic numeric groundedness for testability and to avoid import-time model downloads or paid API calls.

## Remaining Risks and Deferred Work

- The ContextDiff MVP is deterministic and suitable for the seeded gate, but production retrieval should use the platform vector store once the full RAG pipeline is wired.
- The seeded demo intentionally exercises one policy-change scenario; broader corpora need additional fixtures and evaluation rows.
- The UI is a demo surface, not a multi-user review console.
- Provider-backed answer generation remains outside this MVP to keep tests deterministic.

## Proposed Push Command

Run only after explicit approval for the first personal push:

```powershell
git -c safe.directory=D:/ContextDiff push -u origin personal/contextdiff
```

## Commit List on `personal/contextdiff`

- `f725ca1` `feat(rag): implement extraction and chunking pipeline`
- `55681c0` `refactor(rag): address PR review feedback for chunking and ingest`
- `3ba08e4` `chore(format): apply ruff formatting for lint-smoke`
- `2aadb0e` `chore(lint): remove unused TxtExtractor import in rag tests`
- `d977d73` `Implement NLI groundedness and faithfulness guardrail`
- `fe7b35d` `groundness new changes`
- `804d27b` `Repair groundedness review findings`
- `b5c9859` `Address groundedness follow-up review feedback`
- `1066f08` `Add PII and injection guardrails`
- `4599783` `Address PII and injection review feedback`
- `140f154` `Align injection review follow-up details`
- `391de27` `Add ContextDiff MVP release gate`
