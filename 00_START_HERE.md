# 00 — START HERE (single source of truth)

> **Upload this file first to any new Claude/Cowork/Cursor session.** It is the canonical context.
> Companion files: `PROFILE_AND_RESUME.md`, `Buildathon_Intel_and_Strategy.md`. Everything else in this
> folder is reference. If anything conflicts, **this file wins** and should be updated, not the chat thread.

## Who
**Lucky** — AI/ML engineer, ~4 yrs in **regulated AI** (fraud, compliance, claims) at Citi, LPL, Liberty
Mutual/EPAM. Strengths: RAG, agentic workflows (LangChain/LangGraph), LLM eval & governance (Promptfoo,
RAGAS), human-in-the-loop decision systems, hallucination control, AWS/GCP. **Not a beginner** — though the
team leans on heavy AI guidance for production orchestration/integration. Full detail: `PROFILE_AND_RESUME.md`.

## Goals (in priority order)
1. Arrive June 18 with a **reusable agent platform (skeleton)** so the only event-day work is adapting it to the given problem statement + plugging in organizer API credits.
2. A **portfolio/resume/GitHub flagship** with a live link that *compounds the regulated-AI/governance narrative* and reads as engineering maturity to recruiters + judges.
3. A **clean profile** (resume, LinkedIn, GitHub, portfolio site) before the event — separate workstream.
Context: most attendees are visa-holders hunting sponsorship → strong, experienced competition.

## The three workstreams
| # | Workstream | Status | Notes |
|---|---|---|---|
| 1 | **Skeleton** (reusable agent platform) | 🔒 LOCKED — build now | The only thing that directly raises event-day odds. Architecture below. |
| 2 | **Profile / Portfolio / GitHub** | 🔒 LOCKED — run in parallel, **separate Cowork thread** | Recruiters see this before any demo. Resume fixes in `PROFILE_AND_RESUME.md`. |
| 3 | **Flagship** | ▶ ONE decision left (below) | Must compound the governance narrative. No new candidates. |

## ELIMINATED (do not reopen)
GlassHire (recruiting matcher — weaker than existing resume), creator/"AI junior", personal-admin agent,
health concierge, SponsorshipOS. Reason: none compound the regulated-AI story; some are red oceans.

## Flagship — LOCKED 2026-06-10 (rev. 06-10)
**The locked asset is the skeleton.** Skins ride on it and are packaging, not architecture.

- **Locked team asset = reusable trusted-agent platform (skeleton).** Built and integrated end-to-end before the event.
- **Lucky's personal flagship = AI Governance OS** (evolve the deployed **EvidencePack**). Reposition
  "EU AI Act questionnaire" → governance platform: AI-system registry, eval tracking, prompt regression,
  risk scoring, audit trails, evidence-pack export. Compounds the 4-yr resume; judge-native; 30-sec legible.
  **Build this first** — EvidencePack is already live, so it's the fastest path to a portfolio-ready asset.
- **VisaPilot = prepared demo skin, NOT a locked event submission.** Grounded immigration copilot (cite USCIS
  or refuse). Deploy it *only if* the assigned sponsor problem aligns; otherwise it's a reference/demo skin.
- **Event-day submission = whatever sponsor problem statement best fits the skeleton.** Adapt corpus + tools +
  UI copy + workflow on-site. Do not force-fit a pre-chosen product.

**Priority order:** (1) Skeleton — integrated end-to-end (this is what makes skins ~10–15%; if modules are
built in isolation and never merged, skins become 60% pain). (2) Governance OS — fastest, de-risks Lucky's
personal goal. (3) VisaPilot — prepared skin. Profile cleanup = separate thread, later.

## Skeleton architecture (provider-agnostic, build once)
Request → Context builder → Intent router → **Retrieval** (query-expand → embed → vector search → rerank →
select) → **Tools** (Tavily, parsers, custom via a ToolRegistry) → **Reasoning** (draft + citations +
confidence) → **Governance layer** (citation *verification*, confidence scoring, guardrails: injection/PII/
jailbreak) → **Human-review gate** (if confidence < threshold → refuse / route to reviewer) → **Observability**
(traces, latency, cost) → **Evals** (Promptfoo/RAGAS/regression).

Swapping skins changes only **corpus + tools + UI + workflow** (~10–15%); the platform stays ~85% identical.
This is exactly the part that tells Lucky's resume story — keep it the centerpiece.

Default stack: FastAPI/Next.js · Supabase (Postgres + pgvector) · LangGraph · Tavily · **provider-agnostic LLM
abstraction** (so any of the $3k credit providers drop in) · Promptfoo/RAGAS · PostHog/Langfuse · Vercel + a
container host (Railway/Fly/Render) · GitHub Actions.

## Team & ownership (no pro-level expertise → heavy AI assist)
3 now (backend, agentic-workflow, frontend), forming more on-site. **One integrated repo, modular ownership,
merged continuously — NOT assembled on event day** (integration-on-the-day is how teams lose the first 6 hrs):
RAG/retrieval · guardrails/security · evals/observability · frontend/workflow · deployment. Adjust to 3 now.

## Workflow (kills the context-window problem)
- **Repo = source of truth.** GitHub org + `/docs`: `VISION.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md`, `TEAM.md`. Decisions flow into files, not chat threads.
- **Cursor (or Claude Code)** = where code is written — it sits *in the repo*, which is reality. Primary build tool.
- **Claude Cowork** = architecture, planning, project memory, strategy (this is where event intel lives).
- **ChatGPT** = adversarial reviewer (recruiter/investor/critic), not implementation owner.
- **No-code app builders (Lovable/v0/Bolt/Base44/Emergent)** = frontend/dashboard/landing-page acceleration ONLY. Do **not** build the agent core, orchestration, evals, or guardrails in them — they fall over on auth, state, and agent logic.

## Open questions / still-unconfirmed
- $3,000 API credits: which providers/tools (LLMs + vector DB likely; rest TBD — organizer may update). Design provider-agnostic so it doesn't matter.
- Track to select in dashboard: **metadata for filtering/recruiter points, not architecture.** Any serious project spans multiple tracks; pick the track that matches the flagship's center of gravity (Governance OS → Evals & Testing / Security & Guardrails / RAG).
- Venue (Fairview vs Irving) — Lucky handling.
- Final flagship confirm (A vs B).

## File index (this folder)
- `00_START_HERE.md` — this file (canonical).
- `PROFILE_AND_RESUME.md` — resume, project inventory, fixes (new context, was only in chat).
- `Buildathon_Intel_and_Strategy.md` — event facts, companies, judges, predicted problem statements.
- `Flagship_Ideas.md` — idea research (reference; GlassHire/VisaPilot framing predates resume — superseded by the decision above).
- `PROJECT_BRIEF.md` / `CLAUDE.md` — original GlassHire build docs; **superseded**; keep CLAUDE.md's *principles*, repoint the product.
