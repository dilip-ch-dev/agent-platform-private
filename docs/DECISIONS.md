# DECISIONS (ADR log)

Append-only. New decisions flow here, not into chat threads. Format: date · decision · why.

## 2026-06-10
- **Skeleton is the priority asset.** Reusable, provider-agnostic glass-box agent platform. Build once;
  skins ride on it. Rationale: maximizes event-day adaptability; directly showcases the team's/Lucky's strengths.
- **Flagship split (same skeleton underneath):**
  - Lucky personal = **AI Governance OS** (evolve deployed EvidencePack). Compounds resume; judge-native; fastest to portfolio-ready (already live) → build first.
  - **VisaPilot = prepared demo skin, NOT a locked event submission** (rev. 06-10). Deploy only if the assigned sponsor problem aligns. Event submission stays problem-statement-driven; adapt the skeleton on-site.
- **"Skins are ~10–15%" holds ONLY if the skeleton is continuously integrated/merged.** Modules built in isolation → skins become ~60% pain. Integrate end-to-end before the event.
- **GlassHire (recruiting matcher) — KILLED.** Weaker than Lucky's existing resume narrative.
- **Also eliminated:** creator/"AI junior", personal-admin agent, health concierge, SponsorshipOS. Don't compound the governance story / red oceans.
- **Track selection = metadata, not architecture.** Pick the track matching the flagship's center of gravity (Evals & Testing / Security & Guardrails / RAG). Don't let it drive design.
- **Workflow:** repo = source of truth; `/docs` canonical. Cursor/Claude Code = code. Cowork = architecture/PM. ChatGPT = adversarial review. No-code builders = frontend only.
- **Provider-agnostic LLM + pluggable vector store** so the $3k event credits drop in via env.
- **Enemy named: decision thrash.** No new flagship candidates; each would have to beat both locked skins.

## Pending
- Confirm $3k credits coverage (providers/tools) when organizer updates.
- Venue (Fairview vs Irving) — Lucky handling.
- Profile-cleanup workstream — separate thread, after migration.
