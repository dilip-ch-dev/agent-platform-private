# DECISIONS

Append-only. New decisions go here, not into chat threads.

## 2026-06-10

- Skeleton is the priority asset: reusable, provider-agnostic trusted-agent platform.
- Event-day submission remains problem-statement-driven.
- VisaPilot is a prepared demo skin, not a locked event submission.
- Governance OS / EvidencePack is Lucky's personal flagship and separate from the shared team skeleton.
- GlassHire/recruiting matcher is superseded and should not drive repo architecture.
- Repo is the source of truth. Chat threads are not permanent memory.

## 2026-06-11

- Core stack is Python-first: FastAPI + LangGraph + Pydantic.
- Default demo UI is Gradio calling FastAPI over HTTP.
- Next.js is optional later as a polished UI skin, not Phase 0.
- Phase 0 must produce a runnable skeleton with stable contracts and stubbed modules, not a finished product.
- Team work should be split by module slices, but each slice must merge into the same end-to-end API flow.
- JSONL audit logs come before optional PostHog/Langfuse integration.
- Simple/local retrieval comes before pgvector/Supabase integration.
- API-credit providers are useful but must remain behind provider adapters; do not hard-code architecture around any single provider.

## Pending

- Final team member names/handles.
- Final issue assignment after the team reviews `PROJECT.md` and `docs/TEAM.md`.
- Event-day track/problem statement.
