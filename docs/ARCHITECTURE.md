# ARCHITECTURE — trusted-agent skeleton

Provider-agnostic. Build once; adapt later.

The skeleton is the shared team asset. Skins change corpus, tools, workflow, and UI. The core platform should remain stable.

## Default stack

- Core API: FastAPI
- Language: Python
- Contracts: Pydantic
- Orchestration: LangGraph
- Demo UI: Gradio calling FastAPI over HTTP
- Retrieval: pluggable vector interface; local/simple first, Supabase pgvector upgrade path
- Tools: provider adapters, including Tavily where domain rules allow external search
- LLM: provider-agnostic adapter selected by environment variables
- Evals: RAGAS, Promptfoo, or custom scripts
- Observability: JSONL audit logs first; PostHog or Langfuse later

Next.js is optional later as a polished UI skin. It is not Phase 0.

## Data flow

```text
Request
  -> API boundary
  -> Context builder
  -> Intent router
  -> Input guardrail
  -> Retrieval pipeline
  -> Tool layer
  -> Reasoning layer
  -> Governance layer
  -> Human-review or refusal gate
  -> Response
  -> Observability
  -> Evals
```

## Module boundaries

```text
apps/api
  FastAPI service. Owns HTTP boundary, /health, /ask, validation, and OpenAPI docs.

apps/demo
  Gradio demo. Calls FastAPI over HTTP. Does not bypass the API by importing the core directly.

apps/web
  Optional future Next.js skin. Not Phase 0.

packages/contracts
  Shared Pydantic schemas. This is the frozen contract between API, agent, retrieval, governance, and UI.

packages/retrieval
  Ingestion, chunking, search, source locators, citation objects, vector-store abstraction.

packages/agent_core
  LangGraph pipeline, state model, intent routing, reasoning node.

packages/tools
  ToolRegistry and adapters for sponsor tools or custom tools.

packages/guardrails
  Input checks, citation verification, confidence scoring, refusal or review routing.

packages/evals
  Small labeled sets, scoring scripts, RAGAS/Promptfoo adapters.

packages/observability
  JSONL audit log, trace adapters, latency/cost metadata.
```

## Stable contracts

The agent response must be a strict schema with:

- answer or verdicts
- citations
- confidence
- flags
- refusal/review status when evidence is weak

No-evidence is a valid outcome, not an application error.

## Phase 0 architecture goal

Phase 0 should create runnable stubs behind stable contracts, not a finished product.

Acceptance criteria:

- FastAPI boots.
- Gradio boots.
- Gradio calls FastAPI over HTTP.
- `/ask` returns a valid mock response.
- smoke test passes without external network calls.
- no product-specific skin code is added.

## Skin deltas later

Governance OS:
- corpus = regulations, policies, AI-system evidence
- tools = compliance workflows
- UI = governance dashboard
- gate = reviewer approval or evidence gap

VisaPilot:
- corpus = official immigration sources
- tools = visa/deadline helpers
- UI = case dashboard
- gate = cite or refuse

Event-day product:
- adapt the skeleton to the sponsor problem statement
- do not force-fit a prebuilt skin
