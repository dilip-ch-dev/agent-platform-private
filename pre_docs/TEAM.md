# TEAM — collaboration model

We are preparing for a 4-person-ish team where each person may only have 4–5 focused hours before the event. Nobody should build a disconnected mini-app.

## Principle

One integrated repo. Modular ownership. Merge continuously.

The team can split work, but every slice must plug into the same FastAPI + Pydantic contract.

## Repo

- Org: `buildathon-labs`
- Repo: `agent-platform`
- Source of truth: `/docs`, `PROJECT.md`, `CLAUDE.md`
- Work tracking: Linear or GitHub Issues
- Communication: Slack or equivalent

## Natural work slices

Do not assign names here yet. Turn these into Linear/GitHub issues when the team confirms availability.

| Slice | What it owns | Example 4–5 hour outcome |
|---|---|---|
| API + contracts | FastAPI, Pydantic schemas, `.env.example`, smoke test | `/health` and `/ask` return valid schema responses |
| Retrieval | ingestion, chunking, citation objects, search interface | mock/local retrieval returns chunks with source metadata |
| Agent orchestration | LangGraph state, reasoning node, tool registry | pipeline shell runs from request to mock answer |
| Governance + guardrails | input checks, citation verification, confidence score, refusal gate | weak evidence produces low confidence/refusal path |
| Demo + evals + observability | Gradio UI, audit log, small eval set | UI calls API and displays answer, citations, confidence, trace ID |

## How to work remotely

1. Pull latest `main` before starting.
2. Pick one small issue.
3. Create a branch for that issue.
4. Make the smallest working change.
5. Run the smoke test.
6. Open a PR.
7. Merge early after review.

No long-lived branches. No private local masterpieces. No parallel rewrites.

## Definition of done for any slice

A slice is not done because files exist. It is done when:

- it plugs into the shared contract
- it runs locally
- it has a smoke check or minimal test
- it does not introduce real secrets
- it is merged into `main`
- the next teammate can build on it without asking for hidden context

## Suggested issue labels

- api
- contracts
- retrieval
- agent-core
- tools
- guardrails
- evals
- observability
- demo-ui
- docs
- deployment
- blocked

## Pre-event checklist

- [ ] Everyone has repo access.
- [ ] Everyone can clone and run the repo.
- [ ] Phase 0 smoke test passes on at least two machines.
- [ ] Each member has made one small PR.
- [ ] API credit keys are documented in `.env.example`, not committed.
- [ ] Skeleton has one deployed or locally demoable end-to-end path.
