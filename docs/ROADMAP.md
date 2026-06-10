# ROADMAP — to June 18

Priority: **Skeleton first.** It's the only thing that directly raises event-day odds. Skins follow.

## Phase 0 — Repo + foundation (Day 1, ~3h)
- GitHub org + repo; `/docs` (these files) committed; GitHub Projects board (TODO/IN PROGRESS/REVIEW/DONE).
- Next.js/FastAPI scaffold, Supabase project + schema (`documents`, `chunks` w/ pgvector), `.env.example`.
- Provider-agnostic `lib/llm` wrapper with trace logging. Deploy "hello world."

## Phase 1 — Skeleton core (Days 2–4) ⭐ priority
- Ingestion → chunk → embed → store → retrieve (rerank + context select).
- Agent orchestrator (LangGraph) + intent router + ToolRegistry (Tavily).
- Reasoning → typed output (answer/verdicts + citations + confidence).

## Phase 2 — Governance layer (Days 4–5) ⭐ the differentiator
- Citation **verification** (did the answer come from the source — not just "LLM said so").
- Confidence scoring (retrieval + rerank + model + citation coverage).
- Guardrails (prompt injection, PII redaction, jailbreak). Human-review gate (low confidence → refuse/route).

## Phase 3 — Observability + evals (Days 5–6)
- Trace logging → PostHog/Langfuse. Eval harness (labeled set → Promptfoo/RAGAS + regression). Eval dashboard tile.

## Phase 4 — Skins (parallel, after skeleton is stable)
- **Governance OS (Lucky, start first):** reposition EvidencePack → registry + eval tracking + risk scoring + audit trail + evidence export on the skeleton. Live link.
- **VisaPilot (prepared demo skin, not a locked submission):** USCIS/DHS corpus + visa tools + case dashboard; "cite or refuse"; eval dashboard. Deploy only if the assigned sponsor problem aligns.

## Phase 5 — Demo polish + rehearsal (Day 7+)
- Rehearse each demo end-to-end. Freeze. Update resume/GitHub with Governance OS.

## Event day (June 18)
- Pull problem statement → swap corpus/tools/UI/workflow onto the skeleton. <10% time on architecture.

## Parallel (separate thread)
- Profile cleanup: resume fixes, LinkedIn, GitHub, portfolio site (see `PROFILE_AND_RESUME.md`).
