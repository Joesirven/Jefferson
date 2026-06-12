---
date: 2026-06-10
topic: jefferson-architecture-rethink
---

# Jefferson architecture rethink (T9) — requirements

## Summary

The T9 stress-test of Jefferson's standing architecture against the three inbox papers is resolved; this doc carries the rulings forward into the next plan. That plan has exactly two deliverables: a dress rehearsal (the static Wake County backtest) sized to run tonight on the ba-sing-se VPS with a DuckDB warehouse, and a researched decision on which internal data-analytics-agent architecture (OpenAI's or Anthropic's pattern) becomes Jefferson's data foundation. A second plan covering the MVP follows after the rehearsal result.

---

## Problem Frame

T9 mandated re-deriving the best architecture from the canonical `01-ARCHITECTURE` docs plus three unprocessed research items, with all changes flowing as proposed ADRs, never silent edits. The stress-test found no contradictions between the standing decisions and the new research — the papers sharpen the measurement and the planner design rather than forcing a redesign. The open risk was sequencing: planning the expensive layers (voter training, replay pipeline, planner) on unmeasured assumptions. The two-plan loop exists to avoid that: measure first with the cheapest possible experiment, then plan the MVP on the measured gap.

---

## Key Decisions

- **Stress-test posture.** Standing decisions are the null hypothesis; ADRs are proposed only where research or new rulings force a change. No clean-slate re-derivation.
- **v1 scope: snapshot + simple planner + replay-data prep.** v1 includes the race snapshot, a brute-force what-if planner (run candidate interventions through the simulator and rank — no training, no steering), and the start of the replay data pipeline. Amends the standing build sequence; lands as a proposed ADR.
- **Planner Plan A: the hybrid.** A modestly trained, cached strategist proposes moves; every proposal is live-checked at ask-time against the latest data before reaching a campaign; the strategist is retrained incrementally from the last cache, drift-gated, on trusted data only. Trained-RL-only and pure test-time approaches are documented fallbacks. Three caveats are requirements, not notes: (a) proposer and verifier must not share blind spots — use sim-variant disagreement plus periodic real-outcome audits; (b) strategist training data (real campaign actions → outcomes) does not publicly exist and accumulates via the replay pipeline, so the strategist starts dumb; (c) the trained component stays light — the verifier carries the load.
- **Voters: measure first, prep in parallel.** The static rehearsal gates any voter fine-tuning. Replay-data acquisition (old polls, Facebook Ad Library pulls, local news archives) starts in parallel so training data is ready when the gap justifies it.
- **GenMinds adoption is eval-only.** RECAP-style checks (causal traceability, intervention consistency) enter the rehearsal scorecard where cheap. No agent-internals redesign before the gap is measured.
- **QGF is filed, not adopted.** Processed into the research layer; it informs the hybrid planner design but carries no standalone decision.
- **Sentiment keystone gets an owner, not a decision.** The "cheap trusted polling signal" open question (every architectural loop terminates on it) gets a scoped research brief — P2P text-to-web economics, river-sampling bias, MRP on cheap panels. No acquisition strategy is chosen this cycle.
- **Infrastructure: VPS + DuckDB.** The rehearsal and the data warehouse run on the ba-sing-se VPS with DuckDB as the open-source warehouse. Model inference stays serverless per the standing inference ADR. No cloud warehouse.
- **Analytics-agent foundation: decided inside the plan.** Both internal-stack articles are researched against Jefferson's constraints and the plan selects the variant, recorded as a proposed ADR. Early lean, to be pressure-tested rather than assumed: the Anthropic pattern (skills as versioned markdown co-located with transformations, CI-enforced doc updates, semantic-layer-first access) maps onto the existing vault + Meadow + Claude Code setup; the OpenAI pattern (standalone agent, nightly embedded index, memory service) is heavier standing infrastructure for a solo operator.
- **Two-plan loop.** This plan covers only the rehearsal and the foundation decision. The MVP plan (replay pipeline build-out, diffusion, hybrid planner implementation, voter training) is written after the rehearsal result and inherits this doc's decisions.

---

## Requirements

**Dress rehearsal**

- R1. The rehearsal is sized to run tonight; the plan front-loads the one blocking dependency check — whether the NC voter-file archive covers the Nov-2020 as-of date (fallback target per the standing backtest ADR if it fails).
- R2. Every dataset is named with its exact source and access path, and gets a data-registry row (license, PII, provenance, storage) before download, per vault rules.
- R3. The pipeline runs on the ba-sing-se VPS with DuckDB as the warehouse; inference goes through the serverless provider chosen in the standing inference ADR.
- R4. The scorecard adds RECAP-style checks (causal traceability, intervention consistency) where they cost little, alongside the existing per-subgroup error and distributional metrics.
- R5. The deliverable is the measured gap plus a written interpretation; it is the primary input to the MVP plan.

**Analytics-agent foundation**

- R6. The plan researches both internal architectures against Jefferson's constraints: solo operator, DuckDB on a VPS, existing vault + Meadow tooling, Claude Code as the working agent.
- R7. The plan decides the variant (adopt one, or a named hybrid) and records it as a proposed ADR; the foundation must directly serve the rehearsal pipeline rather than stand as a separate project.

**ADRs and research artifacts**

- R8. Every standing-decision change from this brainstorm is drafted as an ADR for explicit sign-off: the build-sequence amendment (v1 scope), planner Plan A (the hybrid), and the analytics-foundation choice.
- R9. The inbox papers are processed into the research layer per the paper template — GenMinds (the commentary thread folds into it) and QGF — and the sentiment-keystone research brief is created with an owner doc.

---

## Scope Boundaries

- The MVP build — replay pipeline build-out, social diffusion, hybrid planner implementation, voter fine-tuning — is documented as decisions here but planned in the second plan, after the rehearsal result.
- Website v2 (T10) and GTM (T11) are outside this doc; they follow the existing redesign brief and execution plan.
- No voter PII enters the vault; no model training occurs before the rehearsal gap is measured.

---

## Dependencies / Assumptions

- NC voter-file archive usability for Nov-2020 is unverified and blocks persona synthesis; the standing backtest ADR names the fallback.
- VPS access is jose-owned paths without sudo; the rehearsal design must not require root.
- The OpenAI article returns 403 on direct fetch; the ByteByteGo deep-dive and the datachain comparison serve as working references until a clean copy is captured into the vault library.
- "Tonight" assumes the dependency check passes quickly and data pulls are small (one precinct, ~300 personas); if the check fails, the rehearsal slips and the plan says so rather than cutting the registry gate.

---

## Outstanding Questions

**Deferred to planning**

- Which analytics-foundation variant wins, and what its minimal v1 surface is (R6–R7 resolve this inside the plan).
- The exact RECAP-check subset that is cheap enough for the rehearsal scorecard (R4).
- Tonight-feasibility checkpoints: where the plan places its go/no-go gates during the evening run.

---

## Sources

- Vault (KB): `01-ARCHITECTURE/Jefferson-Technical-Architecture.md`, `01-ARCHITECTURE/ADRs/` (001–003), `03-MODELS/Backtest-Spec.md`, `05-RESEARCH/_INBOX.md` — paths relative to the Jefferson vault root.
- OpenAI, "Inside our in-house data agent" (Jan 2026): https://openai.com/index/inside-our-in-house-data-agent/ — mirrors: https://blog.bytebytego.com/p/how-openai-built-its-data-agent, https://datachain.ai/blog/openai-anthropic-data-agents
- Anthropic, "How Anthropic enables self-service data analytics with Claude" (Jun 3, 2026): https://claude.com/blog/how-anthropic-enables-self-service-data-analytics-with-claude
- GenMinds/RECAP: arXiv 2506.06958 · QGF: arXiv 2606.11087
