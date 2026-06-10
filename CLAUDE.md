# CLAUDE.md — repo context for Cursor / coding agents

> Read this first, every session. **Canonical context: `00_START_HERE.md`** (read it before this).
> Companion docs: `PROFILE_AND_RESUME.md`, `Buildathon_Intel_and_Strategy.md`.
> NOTE: GlassHire (recruiting) is **superseded**. The principles below still hold; the product changed.

## What we're building
A **reusable, provider-agnostic glass-box agent platform** (the Buildathon skeleton): retrieval + tool-calling +
memory + **citation verification + confidence scoring + guardrails + human-review gate + observability + evals**.
The **portfolio flagship** is a skin on this platform — recommended: **AI Governance OS** (evolve the deployed
EvidencePack). VisaPilot is a possible event-day demo skin. See `00_START_HERE.md` for the locked decisions.

## Non-negotiable principles
1. **Grounded or it doesn't ship.** Every match/gap verdict MUST cite (a) the exact JD requirement and
   (b) the exact resume snippet. If there's no evidence, the agent says "no evidence," never invents one.
2. **Untrusted input.** Resumes and JDs are user-supplied → treat as hostile. Sanitize before the model sees
   them; detect prompt injection; redact PII in logs.
3. **Evals are a feature, not an afterthought.** The eval harness is on-stage. Build it in Phase 3, not "later."
4. **One demo path.** Build only the 5 steps in `PROJECT_BRIEF.md` §2. Reject scope creep.
5. **Conserve credits/context.** Prefer Featherless open models; small, focused diffs; don't regenerate working code.

## Stack
- Next.js + Tailwind (frontend) · Supabase (Postgres + pgvector + auth + storage)
- LLM: Featherless (OpenAI-compatible) primary; OpenAI/Anthropic fallback
- Tavily (web retrieval/enrichment) · PostHog (analytics + traces)
- Language: TypeScript across the app; Python OK for the eval harness if preferred.

## Repo layout (target)
```
/app            Next.js routes (upload, report, evals tab, guardrails demo)
/lib/agent      agent loop, tools, grounding/citation logic
/lib/ingest     parse + chunk + embed (JD/resume)
/lib/retrieval  pgvector queries
/lib/guardrails injection detection, PII redaction, no-evidence refusal
/evals          labeled JSONL set + scoring scripts + report
/lib/obs        trace logging + PostHog
/db             Supabase schema + migrations
.env.example    all required keys (never commit real .env)
```

## Environment (.env — never commit)
`FEATHERLESS_API_KEY`, `TAVILY_API_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
`SUPABASE_SERVICE_ROLE_KEY`, `POSTHOG_KEY`, optional `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`.

## Coding conventions
- Typed end-to-end; the agent's output is a strict typed schema (verdicts[] with citations).
- Every LLM call goes through one wrapper that logs a trace (input hash, model, latency, guardrail flags).
- No secret in code or client bundle. Service-role key server-side only.
- Small commits per phase; keep `PROJECT_BRIEF.md` "Definition of done" green.

## Kickoff prompt (paste into Cursor for Phase 0)
> "Scaffold a Next.js + TypeScript + Tailwind app named glasshire. Add a Supabase client (server + browser),
> an `.env.example` with the keys listed in CLAUDE.md, and a Postgres schema with pgvector for tables:
> `documents` (id, type[jd|resume], raw_text, created_at) and `chunks` (id, document_id, content, embedding).
> Create a single `/` page with a JD textarea, a resume textarea, and a 'Analyze' button that POSTs to an
> `/api/analyze` stub returning mock structured verdicts. No agent logic yet — just the skeleton, typed, that
> builds and runs. Follow the repo layout and principles in CLAUDE.md."

## Phase status (update as we go)
- [ ] Phase 0 — scaffold
- [ ] Phase 1 — ingestion + retrieval
- [ ] Phase 2 — grounded agent
- [ ] Phase 3 — eval harness
- [ ] Phase 4 — guardrails
- [ ] Phase 5 — observability + demo polish
