# CLAUDE.md — Buildathon Agent Platform

This file tells coding agents (and humans) how to work in this repo. Read it before touching any file.

**Truth rule for this document:** sections marked IMPLEMENTED describe code that exists and is tested.
Sections marked TARGET describe the design we are building toward — do not assume that code exists.
Any PR that changes behavior must update this file in the same PR.

---

## What this project is

A problem-agnostic, provider-agnostic RAG/agent skeleton for Buildathon Dallas 2026.
At the hackathon, only config, corpus, and UI skin change — the pipeline code does not.

---

## Stack

| Layer | Technology | Status |
|---|---|---|
| API | FastAPI + Uvicorn | IMPLEMENTED |
| Contracts | Pydantic v2 (strict) | IMPLEMENTED |
| Config | pydantic-settings → `app/config.py` → `cfg` singleton | IMPLEMENTED |
| Guardrails | PII redaction, injection scoring, groundedness (lexical; NLI optional) | IMPLEMENTED |
| Audit | JSONL via `app/audit.py` | IMPLEMENTED |
| UI | Gradio calling FastAPI over HTTP | IMPLEMENTED |
| Evals | corpus + harness against live API | IMPLEMENTED (generic rows) |
| LLM | Provider-agnostic: Anthropic default, any OpenAI-compatible endpoint (e.g. Featherless) via `LLM_PROVIDER` | IMPLEMENTED (registry) |
| Pipeline | LangGraph (`app/orchestration/graph.py`) | TARGET — stub |
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` | TARGET — stub |
| Vector store | ChromaDB (persistent, local) | TARGET — stub |
| NLI verify | `cross-encoder/nli-deberta-v3-base` via `pipeline` extra | OPTIONAL — lazy |
| External verify | Tavily search API | IMPLEMENTED (`external_verify`) |
| Observability | Langfuse (optional extra) | TARGET |

---

## Project structure

```
app/
  config.py                    IMPLEMENTED  single source of truth for all settings
  main.py                      IMPLEMENTED  FastAPI: GET /health, POST /ask (guardrails + audit wired)
  audit.py                     IMPLEMENTED  JSONL audit logger; rejects raw PII keys
  cli.py                       IMPLEMENTED  bt-dev / bt-start / bt-ui / bt-smoke entry points
  guardrails/
    pii.py                     IMPLEMENTED  redact(text) -> (redacted, found_types)
    injection.py               IMPLEMENTED  score(text) -> (float, spans); is_blocked()
    groundedness.py            IMPLEMENTED  verify/split_claims/external_verify
  security/                    TARGET stubs auth.py, tenancy.py, secrets.py
  rag/                         TARGET stubs ingest.py, retrieval.py, chunker.py
  orchestration/               TARGET stubs state.py, graph.py, nodes/pipeline_nodes.py
  tools/                       TARGET stubs registry.py, rag_tool.py, web_search.py
packages/
  contracts/                   IMPLEMENTED  schemas.py, rag.py — frozen Pydantic contracts
ui/
  app.py                       IMPLEMENTED  Gradio demo — calls FastAPI over HTTP only
evals/
  corpus.json                  IMPLEMENTED  30 generic rows (10 answerable / 10 unanswerable / 10 adversarial)
  harness.py                   IMPLEMENTED  runs corpus against live API
tests/
  contracts/  unit/  integration/   97 tests — mirror the app/ structure
data/
  chroma/   audit/             runtime artifacts, git-ignored
scripts/smoke.py               IMPLEMENTED  offline API-contract smoke test
```

---

## Core rules — never break these

1. **Never read `os.environ` directly outside of `config.py`.** Import `cfg` from `app.config` everywhere else.
2. **Never hardcode tunables.** Every threshold/model/path lives in `.env` and is exposed through `cfg`.
3. **Guardrail fail modes are fail-closed.** Unknown `INJECTION_MODE` values block (see `is_blocked`). Do not make fail-open the default anywhere.
4. **Grounded QA must be deterministic.** `REASONING_TEMPERATURE=0.0` in every committed env example. Do not raise it for grounded answering.
5. **The audit log never contains raw PII.** `AuditLogger` rejects payloads with a `question` key — pass `redacted_question`. This is enforced in code and tested.
6. **Ingest must be idempotent** (TARGET — enforce delete-before-insert when `rag/ingest.py` lands; re-uploading a filename replaces, never duplicates).
7. **ChromaDB is persistent, never in-memory** (TARGET — applies when the store lands).
8. **Tests are mandatory.** Every new function or node gets a test before it merges. Guardrail functions are tested with both passing and failing inputs. Unit tests in `tests/unit/`, integration in `tests/integration/`, mirroring `app/`.
9. **PRs only.** No direct commits to `development` or `main`. CI (ruff + pytest + smoke) must be green to merge.

---

## Pydantic contracts (strict)

All data crossing module boundaries must be a Pydantic model. No raw `dict` between packages.

- Input/request models declare `model_config = ConfigDict(strict=True)`.
- `packages/contracts/` never uses `Any`.
- Every endpoint declares `response_model=`; no bare `dict` returns.
- Never mutate a model after creation — use `model_copy(update={...})`.
- Parse external data with `Model.model_validate()`, never `Model(**dict)` on untrusted input.
- Bounded numerics use `Field(ge=, le=)`; enumerated strings use `Literal[...]`.

---

## Pipeline flow (TARGET — Phase 2; input guardrails + audit already live in /ask)

```
input_guardrail (IMPLEMENTED in /ask)
  ├─ blocked → blocked_response → audit → END
  └─ safe → rag_retrieval
               ├─ abstained → abstained_response → audit → END
               └─ evidence found → run_qa
                                     └─ output_guardrail
                                          └─ groundedness_gate
                                               ├─ abstained → abstained_response → audit → END
                                               └─ supported → score_confidence → audit → END
```

Nodes go in `app/orchestration/nodes/pipeline_nodes.py`; wiring in `graph.py` (wiring only, no business logic).
`PipelineState` in `app/orchestration/state.py` is the single contract between nodes.

---

## Guardrails (IMPLEMENTED — see tests/unit/guardrails/)

### PII (`app/guardrails/pii.py`)
- `redact(text, extra_patterns=None)` → `(redacted_text, found_types)` — pure function.
- Detects email, SSN, credit cards (Luhn-checked), phone, IP, API keys.
- Domain types are passed by the caller via `extra_patterns`, not by editing the module.
- Applied inbound in `/ask`; apply outbound to answers when the real pipeline lands.

### Injection (`app/guardrails/injection.py`)
- `score(text)` → `(float, flagged_spans)` — pure; score = MAX of matches, not sum.
- `is_blocked(score, threshold, mode)` — `flag_only` never blocks; unknown modes fail closed.
- Thresholds come from `cfg` at the call site; the module never reads config.
- TARGET: per-chunk scan inside `rag_retrieval` (drop poisoned chunks silently).

### Groundedness (`app/guardrails/groundedness.py`)
- `verify(claim, evidence)` → `"entailment" | "neutral" | "contradiction"`.
  Lexical by default (fast, no heavy deps); `use_nli=True` uses the cross-encoder when the
  `pipeline` extra is installed. Conservative: unsure → neutral → gate abstains.
- `split_claims(text)` → atomic sentences for per-claim verification.
- `external_verify(claim, api_key)` → `(confirmed, url)` via Tavily; no key / network error → `(False, None)`.

---

## Confidence score formula (TARGET — implement with the groundedness gate; re-run eval sweep before changing weights)

```
confidence = 0.5 × groundedness_score + 0.3 × retrieval_scores[0] + 0.2 × citation_coverage
```

---

## How to run locally

```bash
uv sync                       # install (uv only — there is no requirements.txt)
cp .env.example .env          # fill ANTHROPIC_API_KEY / TAVILY_API_KEY as needed
uv run bt-dev                 # API with reload on :8000
uv run bt-ui                  # Gradio demo on :7860 (API must be running)
uv run bt-smoke               # offline smoke test
uv run pytest                 # 97 tests
uv run ruff check .           # lint
uv run python evals/harness.py  # eval corpus against the live API
```

---

## How to skin for the hackathon

Only these change per problem — nothing else:

| What | Where |
|---|---|
| System prompt | `SYSTEM_PROMPT=` in `.env` |
| UI title/placeholder/branding | top of `ui/app.py` |
| Thresholds | `RETRIEVAL_MIN_SCORE`, `GROUNDEDNESS_THRESHOLD`, `INJECTION_THRESHOLD` in `.env` |
| LLM provider | `LLM_PROVIDER` + keys in `.env` (decide by available event credits) |
| Domain PII types | pass `extra_patterns` at the `/ask` call site |
| Demo documents | upload via UI (Phase 1) |
| Domain eval rows | replace generic rows in `evals/corpus.json` |

If the pipeline code needs changing at the hackathon, stop and re-read this file with the team.

---

## Eval corpus

`evals/corpus.json`: 30 generic rows (10 answerable / 10 unanswerable / 10 adversarial).
Generic on purpose — replace with domain rows once the problem statement drops.
Phase 0 expectation: answerable + adversarial pass; unanswerable passes only after
retrieval + the refusal gate land.

---

## Upgrade path (do not implement before gates)

| Flag | Gate | What it enables |
|---|---|---|
| `TENANCY_MODEL=collection_per_tenant` | Gate 1 | Real data isolation |
| `AUDIT_HASH_CHAIN=true` | Gate 1 | Tamper-evident audit log |
| `SECRETS_BACKEND=aws_ssm` | Gate 1 | Keys out of `.env` |
| `EVAL_GATE_ENABLED=true` | Gate 2 | CI blocks on eval regression |
| `RETRIEVAL_RERANK=true` | Gate 3 | Better chunk selection |
| `PII_USE_NER=true` | Gate 3 | Names/orgs via spaCy |
| `REACT_ENABLED=true` | Gate 3 | Multi-step reasoning |
| `CACHE_ENABLED=true` | Gate 3 | Biggest latency lever |
