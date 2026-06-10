# TEAM

3 now (forming more on-site). No professional-level expertise → heavy AI assist (Cursor/Claude Code) for
production orchestration, integration, and execution. Fill names/handles before the event.

## Members & ownership (one integrated repo, modular ownership, merge continuously — NOT on event day)
| Member | Handle | Strength | Owns | Backup |
|---|---|---|---|---|
| _TBD_ | _TBD_ | Backend | `lib/agent`, `lib/llm`, Supabase, deploy | retrieval |
| _TBD_ | _TBD_ | Agentic workflow | `lib/retrieval`, `lib/tools`, `lib/governance` | evals |
| _TBD_ | _TBD_ | Frontend | `app/` UI, both skins, workflow UX | obs dashboard |
| _on-site_ | — | TBD | evals/observability or deploy | — |

> With only 3, evals/observability is shared; whoever finishes their slice first picks it up.

## Repo
- Org: `github.com/<buildathon-team>` · Repo: `skeleton-platform` (skins as `app/governance-os`, `app/visapilot` or branches).
- `/docs` = source of truth (VISION, ARCHITECTURE, DECISIONS, ROADMAP, TEAM). `CLAUDE.md` at root for coding agents.
- Board: GitHub Projects — TODO / IN PROGRESS / REVIEW / DONE.

## Conventions
- Small PRs, reviewed, merged daily. No long-lived branches.
- Every decision → `DECISIONS.md` (not chat). Every architecture change → `ARCHITECTURE.md`.
- All LLM calls go through `lib/llm` (one wrapper, one trace). Never hardcode a provider.
- Secrets in `.env` only (service-role key server-side). Never commit real `.env`.
- Definition of done per slice: typed, traced, has at least one eval/test, merged.

## Tooling
- **Cursor / Claude Code** — write code, in-repo. Primary.
- **Cowork** — architecture, planning, project memory.
- **ChatGPT** — adversarial review (recruiter/judge/investor lens).
- **v0 / Lovable / Bolt** — frontend shells only; wire to backend in Cursor.

## Pre-event checklist
- [ ] Names/handles filled above · org + repo created · everyone has access
- [ ] Each member cloned, ran skeleton locally, made one merged PR
- [ ] `$3k` credit providers confirmed + keys in shared `.env` plan
- [ ] Skeleton deployed; Governance OS live; VisaPilot demoable
