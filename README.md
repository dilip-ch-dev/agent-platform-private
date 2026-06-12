# agent-platform

Reusable Python-first trusted-agent skeleton for Buildathon Dallas 2026.

This repo is the shared team foundation.

## What we are building

A provider-agnostic agent platform with:

- FastAPI API boundary
- Pydantic request/response contracts
- LangGraph orchestration
- retrieval pipeline
- tool registry
- citation verification
- confidence scoring
- guardrails
- refusal or human-review gate
- observability
- eval harness
- Gradio demo UI calling FastAPI over HTTP

## Why

The event problem statement will be released on-site. Instead of guessing the final app now, we are preparing the reusable skeleton so the team can adapt corpus, tools, workflow, and UI quickly.

## Start here

Read these in order:

1. `PROJECT.md` — team-facing overview
2. `docs/00_START_HERE.md` — canonical context
3. `docs/CLAUDE.md` — instructions for coding agents
4. `docs/ARCHITECTURE.md` — technical architecture
5. `docs/TEAM.md` — collaboration model
6. `docs/ROADMAP.md` — phase plan
7. `docs/DECISIONS.md` — decision log

## Current locked stack

- Python core
- FastAPI
- Pydantic
- LangGraph
- Gradio demo UI
- provider-agnostic LLM adapter
- pluggable retrieval/vector store
- JSONL audit logs first
- optional PostHog/Langfuse later


## Phase 0 target

Phase 0 is complete when:

- FastAPI starts locally
- Gradio starts locally
- Gradio calls FastAPI over HTTP
- `/ask` returns a schema-valid mock response
- stable Pydantic contracts exist
- retrieval, agent, tools, guardrails, evals, and observability exist as stubs
- smoke test passes without external API calls
- no secrets or generated artifacts are committed

## Do not build yet

- Governance OS
- VisaPilot
- GlassHire
- final event-day product
- full production dashboard
- provider-specific hard-coded runtime

Those are skins or later phases. Skeleton first.

## Run locally

Prerequisites: Python 3.11 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python scripts/smoke.py
```

Start the API:

```bash
uv run uvicorn apps.api.main:app --reload --host 127.0.0.1 --port 8000
```

Start the Gradio demo (in a second terminal, with the API running):

```bash
uv run python apps/demo/app.py
```

Copy `.env.example` to `.env` and fill in placeholder values as needed. Do not commit `.env`.
