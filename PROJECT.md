# PROJECT — Buildathon Agent Platform

## One-line summary

We are building a reusable Python-first trusted-agent skeleton for Buildathon Dallas 2026.

The goal is to pre-build the reusable foundation so that, once the sponsor problem statement is released, we can adapt corpus, tools, workflow, and UI quickly.

## What is locked

- Team asset: reusable skeleton
- Core stack: Python, FastAPI, LangGraph, Pydantic
- Demo layer: Gradio calling FastAPI over HTTP
- Architecture: provider-agnostic, modular, continuously integrated
- Event product: chosen/adapted after sponsor problem statement drops

## What is not locked

- Final event-day product
- Final UI skin
- Final track strategy
- Final database/vector provider
- Final LLM provider

## Why this approach

Most strong AI applications span several tracks: RAG, agents, evals, guardrails, deployment, observability, and memory. Building disconnected modules creates integration pain on event day. Building one integrated skeleton lets each teammate own a module while still validating the full request flow before the event.

## Core request flow

```text
User/demo request
  -> FastAPI API boundary
  -> Pydantic request/response contract
  -> input guardrail
  -> retrieval pipeline
  -> optional tool calls
  -> LangGraph reasoning pipeline
  -> citation verification
  -> confidence scoring
  -> refusal or human-review gate
  -> structured response
  -> audit log / traces
  -> eval harness
```

## What can be split across the team

Do not treat these as final assignments yet. They are natural work slices that can become Linear/GitHub issues.

### API + contracts

- FastAPI app
- `/health` endpoint
- `/ask` endpoint
- Pydantic request/response models
- `.env.example`
- local smoke test

### Retrieval

- document/text ingestion
- chunking
- source/citation objects
- simple local search first
- vector-store interface for later pgvector/Supabase

### Agent orchestration

- LangGraph pipeline shell
- pipeline state model
- reasoning node
- tool-registry stub
- mock LLM adapter

### Governance + guardrails

- input risk checks
- basic prompt-injection detection
- PII redaction stub
- citation verification stub
- confidence scoring
- refusal/low-confidence gate

### Demo + evals + observability

- Gradio demo calling FastAPI over HTTP
- answer/citation/confidence display
- JSONL audit log
- small eval dataset
- smoke script

## Phase 0 definition of done

Phase 0 is not a full product. It is a working skeleton.

Done means:

- FastAPI starts locally
- Gradio starts locally
- Gradio calls FastAPI over HTTP
- `/ask` returns a schema-valid mock response
- modules exist as stubs behind stable contracts
- `scripts/smoke.py` passes without external API calls
- README explains local setup
- no product-specific skin code is added
- no secrets or generated artifacts are committed

## What to avoid

- Do not build Governance OS in this repo right now.
- Do not build VisaPilot as the default app right now.
- Do not hard-code any LLM provider.
- Do not create disconnected mini-apps.
- Do not optimize UI before the API contract works.

## How we work

- Repo docs are the source of truth.
- Decisions go into `docs/DECISIONS.md`.
- Architecture changes go into `docs/ARCHITECTURE.md`.
- Team ownership goes into `docs/TEAM.md` or Linear/GitHub issues.
- Claude/coding agents should implement small tickets only.
