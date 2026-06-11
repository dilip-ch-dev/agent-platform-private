# ROADMAP — skeleton first

Priority: build the reusable skeleton before any product skin.

## Phase 0 — Shared foundation

Goal: create a tiny but runnable Python-first skeleton.

Deliverables:

- FastAPI app with `/health` and `/ask`
- Pydantic request/response schemas
- Gradio demo calling FastAPI over HTTP
- stub modules for retrieval, agent orchestration, tools, guardrails, evals, and observability
- `.env.example` with placeholder keys only
- `scripts/smoke.py` that passes without external network calls
- README local setup instructions

Do not add Governance OS, VisaPilot, GlassHire, or Next.js in Phase 0.

## Phase 1 — Retrieval foundation

Goal: make the skeleton answer from supplied context.

Deliverables:

- text/document ingestion
- chunking
- source metadata / citation objects
- simple local retrieval first
- vector-store interface for later pgvector/Supabase
- retrieval results passed into the `/ask` flow

## Phase 2 — Agent orchestration

Goal: introduce the LangGraph pipeline.

Deliverables:

- pipeline state model
- intent/router node
- reasoning node
- tool-registry stub
- provider-agnostic LLM adapter
- mock mode for local testing

## Phase 3 — Governance layer

Goal: prove the agent can say no and explain why.

Deliverables:

- citation verification
- confidence scoring
- prompt-injection check
- PII-redaction stub
- low-confidence refusal/review gate
- UI states for answered, refused, blocked, low-confidence

## Phase 4 — Evals + observability

Goal: make reliability visible.

Deliverables:

- JSONL audit logs
- trace ID per request
- small eval dataset
- scoring script
- optional RAGAS/Promptfoo integration
- optional PostHog/Langfuse integration

## Phase 5 — Skin selection / event adaptation

Goal: adapt the working skeleton to the sponsor problem statement.

Possible skins:

- sponsor problem statement skin, chosen on event day
- VisaPilot, only if aligned
- Governance OS, Lucky's separate personal flagship

## Parallel work

- Team setup: Slack/Linear/GitHub access
- API-credit setup: keys and provider docs in `.env.example`
- Profile cleanup: separate private thread, not this shared repo
