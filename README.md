# agent-platform

Reusable Python-first trusted-agent skeleton

## ContextDiff MVP

ContextDiff is a deterministic release gate for RAG answers when source
documents change. It compares corpus version A with version B, maps changed
source units to affected evaluation questions, generates targeted probes,
reruns the same retrieval and answer path against both versions, and emits
`PASS`, `REVIEW`, or `BLOCK` with passage-level evidence.

The seeded demo changes the refund policy from 30 days to 14 days while a
legacy 30-day cache passage remains retrievable in version B. The canonical
demo must return `Release status: BLOCK`.

## What we are building

A provider-agnostic agent platform with:

- FastAPI API boundary with Pydantic contracts
- LangGraph orchestration pipeline
- RAG — ingest, chunk, embed, retrieve (ChromaDB + sentence-transformers)
- Guardrails — PII masking, injection detection, faithfulness gate (NLI)
- Tool registry + Tavily external search
- Confidence scoring and refusal gate
- JSONL audit log and Langfuse observability
- Gradio demo UI

## Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Contracts | Pydantic v2 |
| Orchestration | LangGraph |
| LLM | Anthropic Claude (via LangChain) |
| Embeddings | sentence-transformers — all-MiniLM-L6-v2 |
| Vector store | ChromaDB |
| External search | Tavily |
| UI | Gradio |
| Config | pydantic-settings — reads from `.env` |

## Project structure

```
app/
  main.py               FastAPI — /health, /ask
  config.py             cfg singleton — all settings from .env
  audit.py              JSONL audit logger
  security/             auth, tenancy, secrets
  guardrails/           pii.py, injection.py, groundedness.py
  rag/                  ingest.py, retrieval.py, chunker.py
  orchestration/        state.py, graph.py, nodes/
  tools/                registry.py, rag_tool.py, web_search.py
packages/
  contracts/            shared Pydantic schemas (schemas.py, rag.py)
ui/
  app.py                Gradio demo — calls FastAPI over HTTP
eval/
  harness.py            eval runner
  corpus.json           labeled eval set
data/
  chroma/               ChromaDB store (git-ignored)
  audit/                audit JSONL files (git-ignored)
```

## Local setup

Prerequisites: Python 3.11 and [uv](https://docs.astral.sh/uv/).

```bash
# 1. Install dependencies
uv sync

# 2. Configure
cp .env.example .env
# Fill in ANTHROPIC_API_KEY, TAVILY_API_KEY
```

## Run

```bash
# API
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Demo UI (separate terminal)
uv run python ui/app.py

# Smoke test
uv run python scripts/smoke.py

# ContextDiff canonical demo export
uv run python scripts/contextdiff_demo.py

# Tests
uv run pytest
```

## ContextDiff API

```bash
# Run the canonical seeded demo
curl http://127.0.0.1:8000/contextdiff/demo

# Run with a custom corpus/eval payload
curl -X POST http://127.0.0.1:8000/contextdiff/run \
  -H "Content-Type: application/json" \
  --data @eval/contextdiff_seed.json
```

The API response is a structured JSON report and includes a readable
`html_report` string. `uv run python scripts/contextdiff_demo.py` writes both
formats under `data/audit/contextdiff_demo/`, which is ignored by git.

## Dev vs production

Switch environments via the `ENV` variable:

```bash
# Development (default) — loads .env
ENV=development

# Production — loads .env.production
ENV=production
```

Dev uses `claude-sonnet-4-5` with relaxed thresholds.
Production uses `claude-sonnet-4-7-20250219` with tighter thresholds.

## Adding optional extras

```bash
uv sync --extra pipeline      # transformers + torch (NLI faithfulness gate)
uv sync --extra evals         # ragas
uv sync --extra observability # langfuse
uv sync --extra ner           # spacy (PII NER, Gate 3)
```

## Key rule

Never read `os.environ` directly outside of `app/config.py`. Import `cfg` from `app.config` everywhere else.
