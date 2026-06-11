# agent-platform

Reusable Python-first trusted-agent skeleton for Buildathon Dallas 2026.

This repo is the shared team foundation. It is not the final event-day product, not Lucky's private profile workspace, and not a product-specific app.

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
2. `00_START_HERE.md` — canonical context
3. `CLAUDE.md` — instructions for Cursor / coding agents
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

Next.js is not part of Phase 0. It can be added later as a polished skin if needed.

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
