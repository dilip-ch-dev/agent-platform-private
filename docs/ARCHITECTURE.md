# ARCHITECTURE — glass-box agent platform (skeleton)

Provider-agnostic. Build once; skins swap **corpus + tools + UI + workflow** only (~85% shared).

## Data flow (10 stages)
```
Request
  → Context builder      (user profile, history, memory, project state → AgentContext)
  → Intent router        (need retrieval? tools? memory? workflow? human review?)
  → Retrieval pipeline   (query expand → embed → vector search → rerank → context select)
  → Tool layer           (Tavily, parsers, calculators, custom — via ToolRegistry)
  → Reasoning layer      (LLM → draft_answer + citations + confidence)
  → Governance layer     (citation VERIFICATION, confidence scoring, guardrails: injection/PII/jailbreak)
  → Human-review gate     (confidence < threshold → refuse / route to reviewer)
  → Response
  → Observability        (prompt, docs, tool calls, latency, cost, decision, outcome)
  → Evals                (Promptfoo / RAGAS / regression — every request feeds the harness)
```

## Module boundaries (own one each)
- `lib/llm` — **provider-agnostic** LLM client (OpenAI/Anthropic/Gemini/Featherless behind one interface; switch via env). All calls go through ONE wrapper that logs a trace.
- `lib/retrieval` — embeddings, vector search (pgvector), reranking, context selection.
- `lib/tools` — ToolRegistry; Tavily + document parsers + custom tools.
- `lib/agent` — orchestrator (LangGraph), intent router, reasoning loop.
- `lib/governance` — citation verification, confidence scoring, guardrails, human-review routing.
- `lib/obs` — trace logging + PostHog/Langfuse.
- `evals/` — labeled sets + scoring + regression (Promptfoo/RAGAS).
- `app/` — UI (skin-specific).

## Default stack
FastAPI and/or Next.js · Supabase (Postgres + pgvector) · LangGraph · Tavily · provider-agnostic LLM layer ·
Promptfoo/RAGAS · PostHog (or Langfuse) · Vercel + container host (Railway/Fly/Render) · GitHub Actions.

## Contracts (keep stable so skins don't break the core)
- Agent output is a **strict typed schema**: `verdicts[] | answer` + `citations[]` + `confidence` + `flags[]`.
- "No evidence → refuse" is a first-class path, not an error.
- Every LLM call: one wrapper, one trace (input hash, model, latency, cost, guardrail flags).

## Skin deltas
- **Governance OS:** corpus = regulations/policies; tools = compliance workflows; UI = governance dashboard; gate = reviewer approval.
- **VisaPilot:** corpus = USCIS/DHS .gov; tools = visa/deadline tools; UI = case dashboard; gate = refuse on low confidence.

## $3k credits
Unknown which providers are covered. The provider-agnostic `lib/llm` + pluggable vector store means whatever
they give (LLMs, vector DB) drops in via env — no rework.
