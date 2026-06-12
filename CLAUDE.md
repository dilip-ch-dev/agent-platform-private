# CLAUDE.md — Buildathon Agent Platform

This file tells Claude Code how to work in this repo. Read it before touching any file.

---

## What this project is

Buildathon agent-platform is a problem-agnostic RAG pipeline skeleton built for Buildathon Dallas 2026.
The skeleton handles document ingest, grounded QA, PII masking, injection blocking,
NLI faithfulness verification, and Tavily external fallback.
At the hackathon, only config and content change — the pipeline code does not.

---

## Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Pipeline | LangGraph (`app/orchestration/graph.py`) |
| Embeddings | `sentence-transformers` — `all-MiniLM-L6-v2` |
| Vector store | ChromaDB (persistent, local) |
| LLM | Featherless AI — Llama-3.3-70B (OpenAI-compatible endpoint) |
| NLI model | `cross-encoder/nli-deberta-v3-base` (local, CPU) |
| External verify | Tavily search API |
| Observability | Langfuse (self-hosted via Docker) |
| UI |gradio  
| Config | `python-dotenv` → `app/config.py` → `cfg` singleton |

---

## Project structure

```
app/
  config.py                    single source of truth for all settings
  main.py                      FastAPI: POST /ask, POST /ingest, GET /health
  security/
    auth.py                    FastAPI dependency — verifies requests
    tenancy.py                 resolves tenant_id + principal
    secrets.py                 env / vault loader stub
  guardrails/
    pii.py                     redact(text) → (redacted, found_types)
    injection.py               score(text) → (float, flagged_spans)
    groundedness.py            verify(claim, evidence) + external_verify(claim)
  rag/
    ingest.py                  ingest_file() — extract → chunk → embed → store
    retrieval.py               rag_retrieval(state) → PipelineState
    chunker.py                 stub — chunking logic lives in ingest.py
  orchestration/
    state.py                   PipelineState dataclass — all fields typed
    graph.py                   LangGraph assembly — build_graph() → pipeline
    nodes/
      pipeline_nodes.py        one function per node (9 nodes)
  tools/
    rag_tool.py                stub — wraps retrieval for ReAct (v2)
    web_search.py              stub — Tavily wrapper for ReAct (v2)
ui/
  app.py                       Streamlit UI — skin top section per problem
eval/
  corpus.json                  30-row labeled eval set
  harness.py                   runs corpus against live API
data/
  chroma/                      ChromaDB persistent store (git-ignored)
  audit/                       audit JSONL files (git-ignored)
docker-compose.yml             ChromaDB + Langfuse + Postgres
.env.example                   all config keys with upgrade-path comments
requirements.txt
```

---

## Core rules — never break these

1. **Never read `os.environ` directly outside of `config.py`.** `load_dotenv()` is called once at the top of `config.py` — that is the only place. Everywhere else, import `cfg` from `app.config`.
2. **Never hardcode values.** Every tunable lives in `.env` and is exposed through `cfg`.
3. **`PII_FAIL_MODE`, `INJECTION_FAIL_MODE`, `GROUNDEDNESS_FAIL_MODE` are always `fail_closed`.** Do not change these, do not make them configurable at runtime.
4. **`CHROMA_MODE` is always `persistent`.** Never use in-memory ChromaDB — data would be lost on restart.
5. **`LLM_TEMPERATURE` is always `0.0`.** Grounded QA must be deterministic.
6. **The audit log never contains raw PII.** Only `redacted_question` is written, never `question`.
7. **Ingest is idempotent.** Re-uploading the same filename must replace, never duplicate. The existing delete-before-insert pattern in `ingest.py` enforces this — keep it.
8. **`INGEST_REJECT_BAD_LOCATOR` is always `true`.** Chunks with no resolvable locator cannot be cited — reject them.
9. **Tests are mandatory, not optional.** Every new function or node must have a corresponding test before the code is considered done. No "add tests later" — untested code does not merge. Place unit tests in `tests/unit/` and integration tests in `tests/integration/`, mirroring the `app/` structure. Guardrail functions (`redact`, `score`, `verify`) must be tested with both passing and failing inputs. Pipeline nodes must be tested with mocked state.

---

## Pydantic contracts (strict)

All data crossing module boundaries must be a Pydantic model. No raw `dict` as function arguments or return values between packages.

### Model config

All input and request models must declare strict mode:

```python
from pydantic import BaseModel, ConfigDict

class AgentRequest(BaseModel):
    model_config = ConfigDict(strict=True)
    question: str
    session_id: str | None = None
```

### No `Any` in contracts

`packages/contracts/` must never import or use `Any`. Every field must have a concrete type.

### FastAPI endpoints

Every endpoint must declare `response_model=`. No bare `dict` returns:

```python
# wrong
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

# right
class HealthResponse(BaseModel):
    status: str

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
```

### Never mutate a model after creation

Use `model_copy(update={...})` instead:

```python
# wrong
response.trace_id = trace_id

# right
response = response.model_copy(update={"trace_id": trace_id})
```

### Parsing external data

Always use `Model.model_validate()` for data coming from outside the process (HTTP payloads, file reads, DB rows). Never use `MyModel(**some_dict)` on untrusted input.

### Numeric bounds

All numeric fields with a valid range must use `Field(ge=, le=)`:

```python
confidence: float = Field(ge=0.0, le=1.0)
```

### Status fields

Enumerated string fields must use `Literal[...]`, never bare `str`:

```python
status: Literal["answered", "refused", "blocked", "low_confidence", "review"] = "answered"
```

---

## Pipeline flow

```
input_guardrail
  ├─ blocked → blocked_response → audit → END
  └─ safe → rag_retrieval
               ├─ abstained → abstained_response → audit → END
               └─ evidence found → run_qa
                                     └─ output_guardrail
                                          └─ groundedness_gate
                                               ├─ abstained → abstained_response → audit → END
                                               └─ supported → score_confidence → audit → END
```

All nodes live in `app/orchestration/nodes/pipeline_nodes.py`.
Graph wiring and conditional edges live in `app/orchestration/graph.py`.
**Do not add business logic to `graph.py`** — it is wiring only.

---

## PipelineState

`app/orchestration/state.py` is the single contract between all nodes.
Every field a node reads or writes must exist in `PipelineState`.
If you need a new field, add it there first, then use it in the node.
Never pass data between nodes via global variables or module-level state.

---

## Config flags pattern

All feature flags follow this pattern in `.env`:

```
FEATURE_ENABLED=true/false     # master switch
FEATURE_MODE=...               # behaviour when enabled
FEATURE_FAIL_MODE=fail_closed  # never change
```

When adding a new flag: add it to `.env.example` with a comment, then add it to `app/config.py` as a typed field on `Config`. Never access it anywhere except through `cfg`.

---

## Guardrails

### PII (`app/guardrails/pii.py`)
- `redact(text)` returns `(redacted_text, found_types)` — pure function, no side effects
- Applied inbound (to question) and outbound (to answer) in `pipeline_nodes.py`
- Add domain-specific PII types via `PII_TYPES=` in `.env`, not by editing the regex dict

### Injection (`app/guardrails/injection.py`)
- `score(text)` returns `(float, flagged_spans)` — pure function
- Score = max of all pattern matches (not sum)
- `is_blocked(score)` checks `INJECTION_MODE` — `flag_only` never blocks; set to `block` once tuned
- Per-chunk injection scan happens inside `rag_retrieval` — poisoned chunks are dropped silently

### Groundedness (`app/guardrails/groundedness.py`)
- `verify(claim, evidence)` → `"entailment" | "neutral" | "contradiction"` — uses NLI model
- `external_verify(claim)` → `(confirmed, url)` — calls Tavily, NLI-verifies top result
- `split_claims(text)` splits answer into atomic sentences for per-claim verification
- The gate strips unsupported claims; if nothing remains, it abstains

---

## RAG

### Ingest (`app/rag/ingest.py`)
- Format detection is magic-byte based, not extension-based
- Supported formats controlled by `INGEST_FORMATS` in `.env`
- Chunking: `RecursiveCharacterTextSplitter`, 512 tokens, 64 overlap
- Embeddings: `all-MiniLM-L6-v2` via `sentence-transformers`
- ChromaDB collection name: `tenant_{tenant_id}` — always tenant-scoped

### Retrieval (`app/rag/retrieval.py`)
- Top-k query; scores are `1.0 - L2_distance` (approximate cosine)
- If `scores[0] < RETRIEVAL_MIN_SCORE`, sets `state.abstained = True` before calling LLM
- Per-chunk injection scan applied after retrieval — poisoned chunks dropped

---

## Confidence score formula

```
confidence = 0.5 × groundedness_score
           + 0.3 × retrieval_scores[0]
           + 0.2 × citation_coverage
```

Citation coverage = number of `[` characters in answer / number of claims.
Do not change these weights without re-running the eval sweep.

---

## How to run locally

```bash
# 1. Start infrastructure
docker compose up -d

# 2. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm   # for PII NER (v2, optional now)

# 3. Configure
cp .env.example .env
# Fill in FEATHERLESS_API_KEY, TAVILY_API_KEY, LANGFUSE keys

# 4. Start API
uvicorn app.main:app --reload --port 8000

# 5. Start UI (separate terminal)
streamlit run ui/app.py

# 6. Run eval
python eval/harness.py
```

---

## How to skin for the hackathon

Only these change per problem — nothing else:

| What | File | Time |
|---|---|---|
| System prompt | `SYSTEM_PROMPT=` in `.env` | 30 min |
| UI title, subtitle, placeholder | top section of `ui/app.py` | 30 min |
| Confidence thresholds | `RETRIEVAL_MIN_SCORE`, `GROUNDEDNESS_THRESHOLD` in `.env` | 30 min after sweep |
| Branding colors | `ui/app.py` + `.streamlit/config.toml` | 30 min |
| Domain PII types | `PII_TYPES=` in `.env` | 15 min |
| Demo documents | upload via UI | 1 hour |
| Domain eval rows | `eval/corpus.json` | 2 hours |

Do not edit pipeline code at the hackathon. If the pipeline needs changing, the problem statement is wrong.

---

## Eval corpus format

`eval/corpus.json` contains 30 rows:

```json
{
  "id": "a01",
  "type": "answerable | unanswerable | adversarial",
  "question": "...",
  "expected_abstain": false,
  "expected_blocked": false
}
```

10 answerable, 10 unanswerable, 10 adversarial.
Fill in real domain questions on Day 5 (pre-hackathon) and Hours 8–10 (hackathon domain eval).

---

## Upgrade path (do not implement before gates)

| Flag | Gate | What it enables |
|---|---|---|
| `TENANCY_MODEL=collection_per_tenant` | Gate 1 | Real data isolation between clients |
| `AUDIT_HASH_CHAIN=true` | Gate 1 | Tamper-evident audit log |
| `SECRETS_BACKEND=aws_ssm` | Gate 1 | Keys out of `.env` |
| `EVAL_GATE_ENABLED=true` | Gate 2 | CI blocks on eval regression |
| `RETRIEVAL_RERANK=true` | Gate 3 | Better chunk selection |
| `PII_USE_NER=true` | Gate 3 | Catches names and orgs (spaCy) |
| `REACT_ENABLED=true` | Gate 3 | Multi-step reasoning (do Gates 1+2 first) |
| `CACHE_ENABLED=true` | Gate 3 | Biggest latency lever |

---

## Stub files (to implement per gate)

- `app/security/secrets.py` — Gate 1: vault / SSM loader
- `app/tools/rag_tool.py` — Gate 3: wraps retrieval as a LangGraph tool for ReAct
- `app/tools/web_search.py` — Gate 3: Tavily wrapper for ReAct agent
- `app/rag/chunker.py` — currently inline in `ingest.py`; extract here if chunking logic grows

---

*Buildathon agent-platform .*