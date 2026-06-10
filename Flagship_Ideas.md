# GlassHire → Flagship Idea Shortlist (evidence-backed)

**Constraints every candidate must satisfy:**
- Buildable in ~30–40 hrs by a beginner with heavy AI guidance, before June 18.
- Sits on the **reusable glass-box agent core** (retrieval + tool-calling + memory + evals + guardrails + observability) → so it *also* serves as your Day-1 skeleton.
- Impressive enough for portfolio + resume + GitHub + a live link; ideally fundable.
- Differentiated from the room (judges are agent-infra founders → they reward production rigor, not flash).
- Uses sponsor APIs where possible (Featherless = inference, Tavily = retrieval) for free credits + track relevance.
- **Avoid red oceans** (per research): AI writing tools, resume builders, meeting summarizers, logo gens, generic chatbots, generic productivity. These are saturated and margin-dead.

**Scoring (1–5):** Conviction (can *you* speak to it) · Impress (judge/recruiter wow) · Buildable (in 9 days) · Skeleton-fit (reuses the core) · Distribution (can you get users/attention fast)

---

## ⭐ Candidate 1 — "VisaPilot": a grounded, glass-box copilot for US visa/immigration (OPT, STEM-OPT, H-1B, RFEs)
**The product:** An agent that answers international students'/workers' visa questions and tracks their case —
**every answer cited to the exact USCIS rule/policy memo, or it refuses.** Deadline tracking, document
checklists, RFE-response prep, visa-interview simulation.

**Why this is your strongest play:**
- **Conviction 5** — it's literally *your* world and your peers'. You told me most attendees at this event are on visas seeking sponsorship. You can demo it to the person next to you and they'll *want* it.
- **Distribution 5** — built-in audience at the event. A working link that helps every visa-holder in the room is the most memorable thing you can show a recruiter or judge.
- **Glass-box rigor is the point, not decoration** — wrong immigration info is genuinely harmful, so "cite the official source or say 'no answer'" + guardrails + an eval set scoring citation accuracy is *the feature*. That's exactly the production-agent thesis the Auger/Wand/Microsoft judges reward.
- **Skeleton-fit 5** — it's a RAG + grounded-agent + guardrails + evals app = your Day-1 core in a high-stakes skin.
- **Sponsor fit** — Tavily/Featherless fetch + reason over current USCIS/policy pages; Supabase stores the rule corpus + embeddings.
- **Evidence/why-now:** Kae Capital's "What to Build: Consumer AI" calls study-abroad/immigration copilots a top wedge (≈1M applicants/yr, families spend lakhs on consultants for median work). Immigration tech is a real market (Boundless, Lawfully) — but a *grounded, self-serve, citation-first* copilot for the OPT/H-1B cohort is underserved, and AI now makes it viable.

**Scores:** Conviction **5** · Impress **5** · Buildable **4** · Skeleton-fit **5** · Distribution **5**
**Honest risk:** legal liability. Mitigate by design — "informational, grounded in official sources, **not legal advice**," always show the citation, refuse when confidence is low. (That refusal behavior is your differentiator, not a weakness.) Corpus must be from official .gov sources only.

---

## Candidate 2 — "Glass-box" agent eval + guardrail + observability toolkit (your original idea, productized)
**The product:** An open-source dev tool: drop-in evals, prompt-injection/PII guardrails, and an observability
dashboard for anyone building an AI agent.

- **Conviction 3** (you're newer to devtools) · **Impress 5** (this is literally what Wand/Auger/Featherless/Tavily *sell*; judges' home turf) · **Buildable 4** · **Skeleton-fit 5** (it *is* the skeleton) · **Distribution 4** (open-source GitHub stars = great recruiter signal)
- **Evidence:** IdeaIndex lists "Testing & Monitoring Platform for AI Agents in Production" at Rev 10/10; Preuve names agent infrastructure as a top under-saturated 2026 bet ("picks-and-shovels on the agent gold rush").
- **Risk:** more technical; harder for you to *speak* to deeply at a booth without prep. Best if you lean win-the-track over personal story.

---

## Candidate 3 — "Personal admin agent" (the Rocket Money killer): cancels subscriptions, disputes bills, navigates bureaucracy
- **Conviction 4** · **Impress 5** · **Buildable 2–3** · **Skeleton-fit 4** · **Distribution 4**
- **Evidence:** StartupHeist "Rocket Money Killer" — FTC 100k+ subscription complaints; Rocket Money 10M members, $2.5B saved; browser agents now navigate real sites. Greg Isenberg's #2 = "action apps" (agents that *do*, not display).
- **Risk (big):** "actually executes" means driving real adversarial websites + sometimes credentials/payments. Our safety rules forbid entering financial credentials, and live-site automation is fragile to build reliably in 9 days. Demo-able as a scoped "drafts + guides the cancellation with proof," but the magic part is the risky part.

---

## Candidate 4 — Vertical "AI junior employee" for one creator/SMB role (e.g., podcast/YouTube producer)
- **Conviction 3–4** · **Impress 4** · **Buildable 4** · **Skeleton-fit 5** · **Distribution 3**
- **Evidence:** Greg Isenberg's #6 — "pick a vertical + job title, list the 50 jobs-to-be-done, ship an agent that does them at 1/10th a junior's cost; brand as 'junior,' not replacement." Agentic, fundable, clean story.
- **Risk:** crowded ("a lot of people going after this"); needs a sharp niche to stand out.

---

## Candidate 5 — Condition-specific health concierge (e.g., PCOS) — grounded + guarded
- **Conviction 2–4** (depends on you) · **Impress 4** · **Buildable 3** · **Skeleton-fit 5** · **Distribution 3**
- **Evidence:** Kae Capital wedge — young, digitally-native, underserved cohort self-organizing on Reddit; home tests/CGMs now cheap. Same glass-box rigor (grounded + refuse) applies.
- **Risk:** health data + medical liability; heavier than visa for a 9-day build.

---

## Recommendation matrix

| Idea | Conviction | Impress | Buildable | Skeleton-fit | Distribution | Total |
|---|---|---|---|---|---|---|
| **1. VisaPilot** | 5 | 5 | 4 | 5 | 5 | **24** |
| 2. Glass-box toolkit | 3 | 5 | 4 | 5 | 4 | 21 |
| 3. Personal admin agent | 4 | 5 | 2.5 | 4 | 4 | 19.5 |
| 4. AI junior (creator) | 3.5 | 4 | 4 | 5 | 3 | 19.5 |
| 5. Health concierge | 3 | 4 | 3 | 5 | 3 | 18 |

**Claude's pick: Candidate 1 (VisaPilot).** It's the only one where *your lived experience is the moat*, you have a
captive audience of fellow builders to demo to on the spot, and the glass-box rigor (grounded citations + refusal +
evals) is genuinely required rather than bolted on — which is exactly what this judge panel scores highest. It's also
the cleanest re-skin of the Day-1 skeleton. **Candidate 2** is the strongest pure win-the-track / open-source-signal
fallback if you'd rather not be the face of an immigration product.

> Note: whichever we pick, the underlying core is identical, so we lose nothing by choosing now and can swap skins later.

## Sources
- bigideasdb.com/daily-frustrations-that-need-an-app · markethunt.io reddit analysis · medium "9,300 I-wish posts"
- preuve.ai (dead ideas to revive; 2026 idea ranking) · firstunicornstartup.com YC graveyard · cbinsights startup failures · thefuturelist innovation graveyard
- ideabrowser.com · ideaindex.so (AgentBench Rev 10/10) · kae-capital.com "What to Build: Consumer AI"
- startupheist.com "Rocket Money Killer" · Greg Isenberg (YouTube "9 biggest startup ideas", LinkedIn idea lists) · Product Hunt launches (Goals, ClarifierAI)
