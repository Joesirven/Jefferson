---
date: 2026-06-11
topic: experiment-success-determinants
---

# Experiment success determinants & tracking layer — requirements

## Summary

Define pass/fail thresholds ("success determinants") for Jefferson's experiments, and build the tracking layer that records every experiment run — before any experiment spends money. The first consumer is the dress-rehearsal loop: an automated cycle that runs the Wake County backtest, tweaks, and re-runs until the determinants are met. The holdout rule is part of the definition of done: the experiment passes only when the frozen pipeline also passes on two never-touched precincts (see "The overfitting trap," below).

---

## Problem Frame

The Backtest-Spec deliberately refused to set pass/fail thresholds — its deliverable is "the measured gap." That was right for a one-shot measurement. It breaks the moment the experiment becomes a loop: a loop needs a stop condition, or it runs forever or stops arbitrarily. Meanwhile, competitor research (June 2026) shows the synthetic-polling industry has converged on published accuracy bars and known failure modes, which means Jefferson's determinants can be calibrated against real published numbers instead of guesses. Finally, the vault's eval layer tracks agent-session hygiene only; no system exists to record experiment outcomes run-over-run. That tracking layer must exist before the loop starts, or the iteration history is unrecoverable.

---

## The overfitting trap, in plain language (read this before ruling on the open question)

We know the real answer for the practice precinct. Wake precinct 01-07's certified 2020 result is public — say, for illustration, Biden 58 / Trump 40.

The loop works like this: run the simulation, compare to the real answer, tweak the prompts or personas, run again.

- Run 1: simulation says Biden 51. Error: 7 points. Tweak.
- Run 5: Biden 54. Error: 4 points. Tweak.
- Run 9: Biden 57. Error: 1 point. Stop?

Here is the trap. After nine tweaks made *while looking at the real answer*, a 1-point error is guaranteed to happen eventually — the same way a student retaking the same exam with the answer key in hand eventually scores 100. The score is real; what it proves is not. It proves we sculpted the simulation to fit this one precinct. It does not prove the simulation understands voters.

The fix is the closed-book exam. Take the run-9 version, change nothing — freeze it — and point it at two precincts we never looked at while tweaking (one suburban, one rural; their real 2020 answers are also public, but the loop never used them). Two outcomes:

- The frozen simulation gets them within the (looser) holdout threshold → it learned something real about voters. **Success.**
- It's off by 15 points there → it memorized the practice precinct. **Not success** — back to the loop with better ideas, not just more tweaks.

Why this matters commercially: Aaru — the $1B-valuation competitor in synthetic political polling — publishes accuracy claims nobody can audit ("predicted the NY primary within 371 votes," methodology private), and then called the 2024 battlegrounds wrong. The market has been burned by exactly the claim "trust us, it matched." Jefferson's stated moat in the competitive-landscape doc is *validated* prediction. The closed-book exam is the entire difference between "validated" and "Aaru-style marketing." A pass on unseen precincts survives expert scrutiny; a pass on the practice precinct alone does not.

---

## Key Decisions

- **Thresholds are both relative and absolute.** A pass requires beating both dumb baselines (uniform swing from 2016, demographics-only model) AND hitting the absolute point thresholds below. Protects against "we beat a bad baseline" and "great score, but so was the baseline."
- **Thresholds calibrated to the published industry bar (looser tier).** Matching the field's best published numbers (Verasight 2025: 4-pt average error, 8-pt subgroup) rather than beating them. Achievable for v1 prompting; revisable by ADR after first results.
- **Tracker is DuckDB + a monitoring dashboard UI, built before any LLM spend.** One row per run in the warehouse (source of truth, queryable by the loop) plus a dashboard for watching experiments live. Dashboard design references metric-dashboard patterns pulled from Mobbin. The Pikmin-monitor framing is dropped.
- **Competitive grounding.** No commercial or academic player does precinct-level simulation validated against certified results — Jefferson's lane is empty. The field's three convergent failure modes (subgroup bias, variance collapse, missing "don't know" mass) are exactly what determinants D2 and D3 police.
- **The holdout rule is a hard requirement.** Success is declared only when the frozen pipeline passes on the two never-touched precincts. A practice-precinct-only pass is never announced as "validated." Ruled by Jose, 2026-06-12.

---

## The determinants (Experiment 1: dress-rehearsal loop)

| # | Determinant | Threshold | Source of the number |
|---|---|---|---|
| D1 | Headline accuracy | Two-party vote-share error ≤ 4 pts on practice precinct (≤ 6 pts on holdouts), AND beats both baselines | Industry best published: ~4 pts (Verasight 2025) |
| D2 | Subgroup honesty | Weighted-mean subgroup error ≤ 8 pts; no single group worse than 12 | Verasight's published subgroup bar: 8 pts |
| D3 | Distribution honesty | "Don't know / undecided" present and within 2× the real survey rate; response variance ≥ half the real-survey (CES) variance | Kills the zero-uncertainty and variance-collapse failure modes |
| D4 | Structure | Split-ticket pattern (precinct voted Trump-for-president, Cooper-for-governor or vice versa) reproduced on every scored precinct | The precinct's signature; missing it means wrong mechanism |
| D5 | Generalization | D1–D4 hold (at the looser holdout thresholds) on ≥ 2 untouched holdout precincts with zero pipeline changes | The closed-book exam (see above) — required for overall pass |

Turnout is scored alongside vote share in D1/D2 (same thresholds, both the oracle-weighted and modeled variants reported).

---

## Requirements

**Tracking layer (built first)**

- R1. Every experiment run writes one record: run id, timestamp, git commit, prompt hash, model id, sample count, cost, every D1–D4 metric value, per-determinant pass/fail, free-text notes.
- R2. Records live in the DuckDB warehouse; the loop reads them to decide its next move; nothing about a run is recoverable only from chat or logs.
- R3. A monitoring dashboard shows run history, metric trends across iterations, per-determinant status, and cumulative spend; design referenced against Mobbin metric-dashboard patterns.
- R4. The tracking layer is operational before the first LLM-spending run of the loop.
- R5. The schema is experiment-generic: future experiments (replay, diffusion, planner) define their own determinants but reuse the same run-record shape.

**Loop protocol**

- R6. The loop tunes only on the practice precinct; holdout precincts are never read, scored, or referenced during tuning.
- R7. Each iteration has a spend cap and the loop has a cumulative budget ceiling; hitting the ceiling stops the loop regardless of score.
- R8. The loop's stop conditions are: all determinants pass, budget ceiling hit, or a human stop. No other exit.
- R9. Threshold changes after the loop starts require an ADR — the loop cannot loosen its own goalposts.

**Reconciliation into existing artifacts**

- R10. The determinants and tracking layer amend the dress-rehearsal plan (tracking layer becomes a pre-LLM implementation unit; determinants replace "the deliverable is the gap" as the loop's stop condition, while the gap interpretation write-up remains a deliverable).
- R11. Competitor research lands in the vault: competitive-landscape update (SimSurveys, Aaru, Simile, Expected Parrot, Viewpoints, Verasight benchmark numbers) and the failure-mode papers into the research layer.

---

## Scope Boundaries

- Determinants for future experiments (replay, diffusion, planner) are deferred — only the run-record schema must accommodate them now.
- The dashboard monitors experiments; it is not the campaign-facing product UI and borrows nothing from the website work (T10).
- No public accuracy claims of any kind until D5 status is resolved and, if adopted, passed.

---

## Sources

- SimSurveys methodology & published thresholds: https://simsurveys.com/methodology-evolution (KL < 0.10, JS < 0.05, Spearman > 0.75; paired live-vs-synthetic design)
- Verasight synthetic-sampling white paper (the industry's honest benchmark: 4-pt avg / 8-pt subgroup / 15-pt minority-group error, ~0% don't-know vs 29% real): https://www.verasight.io/reports/synthetic-sampling
- Aaru 2024 battleground misses: https://www.semafor.com/article/11/04/2024/an-ai-polling-startup-polls-bots-predicts-harris-will-win
- Park et al., "Generative Agent Simulations of 1,000 People" (86% individual replication, interview-conditioned): https://arxiv.org/abs/2411.10109
- Failure-mode literature: variance collapse & homogenization (arXiv:2507.02919), social-desirability bias (arXiv:2405.06058), silicon sampling foundations (arXiv:2402.18144)
- Vault: `03-MODELS/Backtest-Spec.md` (existing metrics this doc adds thresholds to), `04-PRODUCT/Jefferson-Competitive-Landscape.md` (moat claim), `00-OPS/EVALS.md` (session-level eval layer this does not replace)
- Companion doc: `docs/brainstorms/2026-06-10-jefferson-architecture-rethink-requirements.md` (the dress-rehearsal scope this amends)
