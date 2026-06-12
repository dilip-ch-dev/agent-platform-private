# agent-platform

Reusable Python-first trusted-agent skeleton for Buildathon Dallas 2026.

## What works today

- FastAPI API boundary (`/health`, `/ask`) with strict Pydantic contracts
- Input guardrails wired into `/ask`: PII redaction + prompt-injection blocking
- Groundedness verification utilities (lexical now, NLI optional, Tavily external check)
- JSONL audit logging (raw PII mechanically rejected)
- Gradio demo UI calling the API over HTTP
- Eval corpus (30 rows) + harness; 91 tests; ruff + pytest + smoke in CI

## What is planned (stubs in place)

RAG ingest/retrieval (ChromaDB + sentence-transformers), LangGraph pipeline,
auth/tenancy, tool registry. See `CLAUDE.md` for the status-marked breakdown.

## Stack

| Layer | Technology |
|---|---|
| API | FastAPI + Uvicorn |
| Contracts | Pydantic v2 (strict) |
| Config | pydantic-settings — `.env` → `cfg` singleton |
| Guardrails | regex PII + injection scoring + lexical/NLI groundedness |
| LLM | provider-agnostic: Anthropic default, any OpenAI-compatible endpoint (Featherless etc.) via `LLM_PROVIDER` |
| Orchestration | LangGraph (planned) |
| Vector store | ChromaDB (planned) |
| External search | Tavily |
| UI | Gradio |

## Local setup

Prerequisites: Python 3.11 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
cp .env.example .env   # fill in ANTHROPIC_API_KEY / TAVILY_API_KEY as needed
```

## Run

```bash
uv run bt-dev                    # API with auto-reload on :8000
uv run bt-ui                     # Gradio demo on :7860 (separate terminal)
uv run bt-smoke                  # offline smoke test
uv run pytest                    # test suite
uv run ruff check .              # lint
uv run python evals/harness.py   # eval corpus against live API
```

First time on a clone? Also run `uv run pre-commit install` so lint,
line-ending, and secret checks run on every commit.

## Dev vs production

`ENV=production` loads `.env.production` (if present); anything else loads `.env`.
Keep `REASONING_TEMPERATURE=0.0` — grounded QA must be deterministic.

## Optional extras

```bash
uv sync --extra pipeline      # transformers + torch (NLI faithfulness gate)
uv sync --extra evals         # ragas
uv sync --extra observability # langfuse
uv sync --extra ner           # spacy (PII NER, Gate 3)
```

## Key rules

- Never read `os.environ` outside `app/config.py` — import `cfg` instead.
- PRs only; CI must be green to merge. See `CLAUDE.md` for the full ruleset.
