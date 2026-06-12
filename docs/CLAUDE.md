# CLAUDE.md — coding-agent instructions

> Read `docs/00_START_HERE.md` before this file. This repo is the shared Buildathon skeleton, not a product-specific app.

## What we are building

A reusable, provider-agnostic trusted-agent platform for the Buildathon.

The platform should support:

- retrieval
- tool use
- grounded reasoning
- citation verification
- confidence scoring
- guardrails
- human-review or refusal gate
- observability
- evals

The event-day submission remains problem-statement-driven. VisaPilot is only a prepared demo skin. EvidencePack / Governance OS is Lucky's personal flagship and should not dictate the team skeleton stack.

## Locked stack

- Core language: Python
- API: FastAPI
- Contracts: Pydantic
- Orchestration: LangGraph
- Demo UI: Gradio, calling FastAPI over HTTP
- Retrieval: pluggable vector store; local/simple first, Supabase pgvector later
- LLM: provider-agnostic adapter selected through environment variables
- Evals: RAGAS, Promptfoo, or custom scripts
- Observability: JSONL audit logs first; PostHog or Langfuse later

Do not scaffold Next.js or TypeScript in Phase 0. Next.js can be an optional polished skin later.

## Non-negotiables

1. Build the skeleton before skins.
2. Keep a stable Pydantic request and response contract.
3. Every module must plug into the same FastAPI boundary.
4. Gradio must call FastAPI over HTTP, not bypass the API by importing core functions directly.
5. Do not create product-specific code for Governance OS, VisaPilot, or recruiting in Phase 0.
6. Keep commits small and reviewable.
7. Never commit real secrets or local environment files.

## Target repo layout

```text
apps/
  api/                 FastAPI service
  demo/                Gradio demo UI calling FastAPI
  web/                 optional future Next.js skin, not Phase 0

packages/
  contracts/           Pydantic schemas shared across modules
  retrieval/           ingestion, chunking, search, citations
  agent_core/          LangGraph pipeline and orchestration
  tools/               tool registry and sponsor-tool adapters
  guardrails/          input checks, citation verification, confidence gate
  evals/               eval datasets and scoring scripts
  observability/       audit logs and trace adapters

docs/                  source of truth
scripts/               smoke checks and local helpers
.env.example           example keys only
```

## Phase 0 Cursor prompt

Paste this into Cursor only after the working tree is clean:

```text
Read docs/00_START_HERE.md, docs/CLAUDE.md, docs/ARCHITECTURE.md, docs/DECISIONS.md, docs/ROADMAP.md, and docs/TEAM.md.

Scaffold Phase 0 only.

Build a Python-first monorepo skeleton:
- FastAPI app in apps/api with /health and /ask endpoints
- Gradio demo in apps/demo that calls the FastAPI /ask endpoint over HTTP
- Pydantic schemas in packages/contracts
- stub modules for retrieval, agent_core, tools, guardrails, evals, and observability
- .env.example with placeholder keys only
- scripts/smoke.py that validates the API contract without external network calls

Constraints:
- no Next.js or TypeScript in Phase 0
- no product skin code
- no real API calls
- no secrets
- no generated artifacts committed
- keep the scaffold small, typed, and runnable

Acceptance criteria:
- python scripts/smoke.py passes
- FastAPI starts locally
- Gradio starts and calls FastAPI
- README explains how to run locally
```

## Phase status

- [ ] Phase 0 — Python skeleton scaffold
- [ ] Phase 1 — ingestion + retrieval
- [ ] Phase 2 — grounded agent
- [ ] Phase 3 — eval harness
- [ ] Phase 4 — guardrails + confidence gate
- [ ] Phase 5 — observability + demo polish
