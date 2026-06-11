# Buildathon Dallas 2026 — Intel & Strategy (Source of Truth)

**Owner:** Team · **Role:** AI/ML engineer (builder) · **Goal:** Win a track + get recruited
**Prep window:** ~25 hrs before June 18 ·
**Last updated:** 2026-06-09 · 

> This is the single source of truth. Update it as facts change. Load it into coding agents/preferred IDEs at the
> start of every build session so context stays consistent and we don't re-derive or hallucinate.

---

## 0. Confidence legend
- ✅ **Confirmed** (seen on buildathon.co or first-party company site)
- 🟡 **Likely** (strong inference from who's in the room)
- 🔴 **Unverified / conflicting** (do not rely on without checking)

---

## 1. Event facts

| Item | Value | Conf. |
|---|---|---|
| Dates | June 18–19, 2026 (32 hrs) | ✅ |
| Build window | ~24 hrs, starts ~12:00 PM Day 1 | ✅ |
| Venue | **CONFLICT:** Eventbrite = The Meridian Venue, Fairview TX 75069; site/Luma copy = Irving TX | 🔴 |
| Headcount | Marketed "1,000+ / 1,500+ / 1,800+" — inflated; Partiful shows ~26 confirmed | 🔴 |
| Format | Pick a track → get a sponsor problem statement → build on-site → Match Day demo | ✅ |
| Judging axes | Execution, architecture, product thinking, deployment quality, real-world usability | ✅ |
| Rule | Build the sponsor problem statement on-site; **cannot submit a pre-built project** | ✅ |
| Loophole | A pre-built **flagship in your profile** is fine for recruiting + fallback showcase | ✅ (per your read) |

**Run of show:** 9:00 doors · 10:00 opening · 10:30 sponsor & track intros · 11:30 team formation · 12:00 build starts · +24 hrs · Match Day (recruiters, VCs, founders, eng leaders).

**Site bug note:** buildathon.co only renders on Firefox + mobile; dead on Chromium (Chrome/Brave/Edge). Crawlers get 404s/empty shells. Minor signal on organizer eng maturity; irrelevant to our build.

---

## 2. The 10 tracks ✅
1. Frontend & UX
2. Agent Orchestration
3. RAG & Retrieval
4. LLM Inference
5. Memory & Context
6. Voice & Audio
7. Data Pipelines
8. Evals & Testing
9. Deployment & MLOps
10. Security & Guardrails

---

## 3. Companies "Already in the Room" ✅ (with what they actually do)

> **Critical correction:** an earlier Buildathon LinkedIn post name-dropped Amazon, JPMorgan,
> Walgreens, Verizon, AT&T, Findem, RippleMatch. **None are on the official site list.** This is a
> **startup + dev-tool room**, not a Fortune-500 room. Only Walmart, Tech Mahindra, Microsoft are
> true enterprises (and CVS appears only as a *judge's employer*). Strategy is built on the real list.

### Dev-tool / AI-infra (these likely own technical tracks & give API problem statements)
- **Lovable** — AI app/vibe-code builder. → **Frontend & UX**.
- **Featherless AI** — serverless inference for 30k+ open LLMs, flat pricing, $20M Series A. → **LLM Inference / Deployment & MLOps**.
- **Tavily** — web search/extraction/retrieval API for agents; built-in PII/prompt-injection safeguards. → **RAG & Retrieval** (and **Security & Guardrails**).
- **TinyFish** — enterprise web agents: search, fetch, real-browser, authenticated multi-step workflows, deterministic success/fail signals. (Listed as early partner.) → **Agent Orchestration / RAG**.

### Agentic / vertical AI startups (founders are mostly judges → see §4)
- **Geodo** — 🟡 AI GTM "digital twin" sales agent (geodo.ai, backed by Sam Altman). *Ambiguity:* a geodo.tech also exists (drone RTK/GIS). Judge Nadav Shanun = "Founder, Geodo." → **Agent Orchestration**.
- **Cartie AI** — agentic commerce as a service: embeddable checkout / "buy now" for AI surfaces, ACP/UCP protocols. (cartie-ai.com "launching soon"; related docs at cartai.ai.) → **Agent Orchestration / Frontend**.
- **Klerk (KlerkAI)** — no/low-code AI agents for workflow automation: doc processing, email, data entry, CRM/Slack integration. → **Agent Orchestration**.
- **CallFort** — AI scam-call/text blocking; real-time fraud intelligence for consumers + telecom/fin. Judge Rob E = CEO. → **Security & Guardrails / Voice & Audio**.
- **Efficast** — industrial IoT: real-time factory/OEE monitoring + "MAIA" AI supervisor over PLC/sensor data (hardware + software, Argentina). → **Data Pipelines**.
- **Pipecode (PipeCode.AI)** — data-engineering interview-prep platform: real Qs, AI mock interviews, resume builder. Judge Nikhil Gurram = CEO. → **Data Pipelines / recruiting-edtech**.
- **Just Videos Studios / CTE (Cinematic Thinking Engine)** — video/media AI. Judge = Co-founder/CTO. → **Frontend & UX / media**.
- **GiraffyReach** — real-time job-search + automated recruiter-outreach copilot; crawls 66k career pages, surfaces recruiter emails, tracks PDF opens. Judge Sai Pavan = founder. → **RAG/Data + recruiting**.

### Enterprises
- **Walmart** — retail. 🟡 likely a retail/ops/associate-assistant problem statement.
- **Tech Mahindra** — IT services/consulting; judge AK Denduluri = VP Transformation Advisory. 🟡 enterprise-automation prompt.
- **Microsoft** — judge Sudarshan = Principal AI Eng Mgr, Dynamics 365. 🟡 Azure/Copilot-adjacent.

### Services / VC / other
- **SeedLegals** — legal + cap-table automation for startups; judge Anthony = CEO.
- **elmnts.vc** — $40M early-stage fund; thesis = **real-asset, industrial, hardtech, regulated markets** ("domain depth is the moat," won't invest outside it). Judge Somya Gupta = partner. ⚠️ *Do not pitch generic AI SaaS to this judge — frame for hard/regulated industries.*
- **SDVS Technologies** — IT services; judge Divya Budda = CEO.
- **FoundersPrime.com** — 🔴 unverified (likely founder services).
- **Omniverse City** — 🔴 unverified (likely 3D/metaverse).
- **GEODO** (logo tile) — see Geodo above.
- **Hashtag India** — food vendor (ignore).

---

## 4. Judges (✅ from screenshots) + leverage notes

| Judge | Role / Company | What they'll reward | Recruiting angle |
|---|---|---|---|
| **Sandeep Nutakki** | Sr AI Engineer, **Auger** ($100M, autonomous supply-chain, ex-Amazon) | Autonomous execution, "glass-box" guardrails, ontology/data-truth | High — hiring AI eng |
| **Sudarshan** | Principal AI Eng Mgr, **Microsoft** Dynamics 365 | Production architecture, enterprise patterns, reliability | High |
| **Rohit Desai** | SDE (ICT3), **Apple** | Clean engineering, performance, polish | High |
| **Somya Gupta** | **Wand AI** (agentic-workforce OS) + Partner, **elmnts.vc** | Multi-agent governance/oversight; for VC lens → hard/regulated markets | High (job + capital) |
| **Sreenivasa Reddy V** | Sr Data Engineer, **CVS Health** | Data pipelines, healthcare-grade rigor | Med-High |
| **Ajit Rajendran** | Sr SWE, **Esri** (GIS) | Solid software, geospatial bonus | Med |
| **Mufeng Xie** | SWE, **Kikoff** (fintech credit) | Fintech reliability, correctness | Med |
| **Nikhil Gurram** | CEO, **PipeCode.AI** (DE interview prep) | Data-eng depth, recruiting/edtech | Med |
| **Lakshmi K. Guduru** | Founder, **Cartie AI** (agentic commerce) | Agentic commerce, embeddable UX | Med |
| **Nadav Shanun** | Founder, **Geodo** (GTM agent) | GTM/sales agents, personalization | Med |
| **Sai Pavan Kumar** | Founder, **Giraffy Reach** (recruiting AI) | Real-time data + outreach automation | Med |
| **Rob E.** | CEO, **CallFort** (anti-fraud) | Fraud/guardrails, telecom security | Med |
| **Divya Budda** | CEO, **SDVS Technologies** (IT services) | Practical delivery | Med |
| **AK Denduluri** | VP, **Tech Mahindra** | Enterprise transformation, scale | Med |
| **Anthony** | CEO, **SeedLegals** | Product thinking, startup/legal automation | Low-Med |
| **Jigisha Bagchi** | Principal Attorney, Bagchi Law / LegalX OS | Legal-tech, compliance | Low |
| **(CTE / Just Videos)** | Co-founder/CTO (name cut off) | Media/video AI, creative | Low |

**Pattern that matters most:** the heaviest-hitting technical judges (Auger, Wand AI, Microsoft, Apple, TinyFish-adjacent) all live in **production-grade autonomous agents with governance, observability, and guardrails** — not flashy demos. Wand's entire thesis is *governing* agents; Auger's is *autonomous execution inside a "glass box."* **Reliability + evals + guardrails will out-score visual polish in this room.**

---

## 5. Predicted problem statements per track (🟡 inference)

| Track | Likely sponsor owner | Predicted problem statement (our best guess) | Confidence |
|---|---|---|---|
| Frontend & UX | Lovable | "Generate a usable production UI for [X] from a prompt; judged on real usability" | 🟡 |
| Agent Orchestration | Wand AI / Auger / Klerk / TinyFish | "Build a multi-step agent that executes a real workflow with oversight & recovery" | 🟡 high |
| RAG & Retrieval | Tavily / TinyFish | "Build an agent that answers over live web/private docs with grounded citations, no hallucination" | 🟡 high |
| LLM Inference | Featherless AI | "Build on open models via our API; optimize latency/cost/routing across models" | 🟡 high |
| Memory & Context | (Auger/Wand-flavored) | "Give an agent persistent, queryable memory across sessions/users" | 🟡 |
| Voice & Audio | CallFort | "Real-time voice agent or scam/fraud detection on calls" | 🟡 |
| Data Pipelines | Efficast / CVS / PipeCode | "Ingest messy real-time/operational data → clean, queryable, actionable" | 🟡 |
| Evals & Testing | Wand / general | "Build an eval/regression harness that scores agent quality automatically" | 🟡 high |
| Deployment & MLOps | Featherless / general | "Ship + monitor a model/agent in production with scaling & observability" | 🟡 |
| Security & Guardrails | CallFort / Tavily / Wand | "Defend an agent against prompt injection / PII leak / unsafe actions" | 🟡 high |

---

## 6. Flagship candidates (decision pending — your call)

Scored 1–5 on: **Overlap** (with likely problem statements), **Recruit** (appeal to hiring judges),
**Buildable** (in 30–40 hrs with heavy guidance), **Judge-fit** (resonance with the room's thesis).

### Candidate A — "Glass-box agent platform": a reliable agent + eval + guardrail harness
A vertical agent (e.g., over support docs or live web) shipped **with** an automatic eval suite,
prompt-injection/PII guardrails, and an observability dashboard. Built on Tavily (retrieval) +
Featherless/your LLM + Supabase + PostHog.
- Overlap **5** (spans Agent Orchestration, RAG, Evals, Guardrails — 4 tracks) · Recruit **5** (this is literally Wand/Auger/MSFT/Apple's world) · Buildable **3** (ambitious; scope to one demo path) · Judge-fit **5**
- **Why it wins:** matches the single strongest pattern in the room. Risk: breadth — must scope hard.

### Candidate B — Recruiting/talent agent (the meta-play)
An agent that does something sharp in hiring (e.g., live JD↔resume matching with grounded
evidence + outreach drafting), overlapping GiraffyReach + PipeCode + the event's own purpose.
- Overlap **4** · Recruit **5** (you're at a recruiting event; judges literally run recruiting tools) · Buildable **4** · Judge-fit **4**
- **Why it wins:** doubles as your own job-hunt weapon. Risk: GiraffyReach/PipeCode founders may see it as "their" space — differentiate on rigor.

### Candidate C — Industrial/ops autonomous agent (for the elmnts.vc / hard-industry lens)
Agent over operational/IoT-style data (Efficast/Auger flavor) that detects→decides→acts with guardrails.
- Overlap **4** · Recruit **4** · Buildable **2** (needs realistic data; hardest in 30–40h) · Judge-fit **4** (great for Somya/elmnts + Auger)
- **Why it wins:** strongest VC-funding angle. Risk: data realism is hard without a real feed.

**Claude's recommendation:** **Candidate A**, scoped to ONE bulletproof vertical demo path, because it
(a) overlaps the most predicted problem statements, (b) is exactly what the top hiring judges build, and
(c) the eval+guardrail layer is the differentiator almost no hackathon team ships. Candidate B is the
strong runner-up and the better pure-recruiting play. **Decision is yours — see §8.**

---

## 7. Tooling & connectors (current)
- **Connected:** GitHub (via plugin), Slack, Linear, Notion, Supabase, Exa, PostHog. Plugins: engineering, product-management, twilio-developer-kit.
- **Not needed yet:** more connectors. The one gap is an **LLM API key** (OpenAI/Anthropic/Featherless) — lives in code `.env`, never a Cowork connector.
- **Build IDE:** Cursor ($20/mo) for codegen; Cowork (here) for strategy/research/architecture/orchestration. Add Claude API credit only if the *app itself* calls Claude at runtime.

## 8. Decisions — UPDATED 2026-06-10 (see `00_START_HERE.md` for canonical)
1. ✅ **Skeleton = the asset:** reusable, provider-agnostic glass-box agent platform (retrieval + tools +
   memory + citation verification + confidence + guardrails + human-review + observability + evals). Build now.
2. ✅ **GlassHire (recruiting) — SUPERSEDED.** Resume context shows Lucky is a regulated-AI engineer; the
   flagship must compound the governance narrative, not introduce recruiting.
3. ▶ **Flagship — one decision left:** **A) AI Governance OS (evolve EvidencePack) — recommended** vs
   **B) VisaPilot (event demo skin).** Both ride the same skeleton.
4. ✅ **Three workstreams:** Skeleton · Profile/Portfolio (separate thread) · Flagship. Enemy = decision thrash.
5. ✅ **Workflow:** repo = source of truth; Cursor/Claude Code for code; Cowork for architecture; ChatGPT
   adversarial; no-code builders for frontend only. Track choice = metadata, not architecture.
6. ⬜ **Unconfirmed:** $3k credits coverage; venue (Lucky handling).

## 9. How we work (workflow guardrails)
- This `.md` is the source of truth. New facts → update here, not buried in chat.
- Keep this chat for decisions; do heavy iterative coding in IDEs/agents to save context + credits.
- I keep a visible task list so progress is always legible.

## 10. Sources
- buildathon.co (Tracks, Judges, Companies — provided via screenshots/manual paste, site renders only on Firefox/mobile)
- Eventbrite, Luma, Partiful event listings; Buildathon Inc LinkedIn (⚠️ company list there is inflated/inaccurate vs site)
- First-party company sites: featherless.ai, tavily.com, tinyfish.ai, geodo.ai, cartai.ai, klerk (AgentLocker/Creati), callfort (Prospeo), efficast.ai, pipecode.ai, auger.com, wand.ai, elmnts.vc, giraffyreach.com
