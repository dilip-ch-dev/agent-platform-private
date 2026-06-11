# 00 — START HERE

> Read this file first in every planning or build session. It is the team-level source of truth for this repo.
> If anything conflicts, update this file and `docs/DECISIONS.md` instead of relying on chat history.

## Repo purpose

This repo contains the shared Buildathon skeleton: a reusable, provider-agnostic trusted-agent platform.

It is not a personal profile workspace and it is not a pre-committed final event product. The event-day submission will adapt to the sponsor problem statement.

## Goals

1. Build a reusable skeleton before the event.
2. Keep the architecture flexible enough to support multiple tracks and sponsor tools.
3. Allow teammates to work in parallel on clear modules without creating disconnected mini-apps.
4. Make the system demoable through one end-to-end request flow before adding skins or polish.

## Locked decisions

- The team asset is the skeleton.
- The core is Python-first: FastAPI + LangGraph + Pydantic.
- The default demo UI is Gradio calling FastAPI over HTTP.
- Next.js is optional later as a polished skin, not Phase 0.
- VisaPilot is only a prepared demo skin if the sponsor problem aligns.
- Governance OS / EvidencePack is a separate personal flagship, not the driver of this team repo.
- No product-specific skin should be built until the skeleton runs end-to-end.

## Skeleton architecture

```text
Request
  -> FastAPI boundary
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

## Default stack

- API: FastAPI
- Contracts: Pydantic
- Orchestration: LangGraph
- Demo UI: Gradio
- Retrieval: pluggable vector/search interface
- LLM: provider-agnostic adapter
- Tools: Tavily and other sponsor/custom tools through adapters
- Evals: RAGAS, Promptfoo, or custom scripts
- Observability: JSONL audit logs first; PostHog/Langfuse optional later

## Team work model

Work can be divided into module slices, but every slice must plug into the same API contract.

Possible slices:

- API + contracts
- retrieval
- agent orchestration
- tools
- guardrails + confidence
- evals + observability
- demo UI
- deployment

Assignments should be made in Linear/GitHub Issues after the team reviews `PROJECT.md` and `docs/TEAM.md`.

## Workflow

- Repo docs are the source of truth.
- Decisions go in `docs/DECISIONS.md`.
- Architecture goes in `docs/ARCHITECTURE.md`.
- Team workflow goes in `docs/TEAM.md`.
- Any coding agent or IDE is acceptable if it follows the repo docs.
- No-code builders may help with UI shells only, not the core agent pipeline.
- Chat threads are for clarification and review, not permanent memory.

## Current priority

Phase 0 only:

- FastAPI app
- Pydantic contracts
- Gradio demo calling the API
- stubbed retrieval, agent, tools, guardrails, evals, and observability modules
- local smoke test

Do not build final product skins yet.
