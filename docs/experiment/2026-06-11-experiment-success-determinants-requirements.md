# Experiment success determinants — requirements

**Audience:** project owner (not an AI engineer).  
**Experiment:** dress-rehearsal backtest — simulate Wake County, North Carolina precincts for the 2020 election and compare simulated vote shares to real results.  
**Last updated:** 2026-06-12 (rebuilt after stranded Claude session; research conclusions incorporated).

---

## What we are trying to prove

Jefferson builds **synthetic voters** (AI personas with demographics, party, issues, news habits) and **polls them** as if they were real people. The dress rehearsal asks a simple question:

> When we simulate ~300 voters in a precinct we have **never used for tuning**, do the simulated results land close enough to what actually happened in 2020?

If yes — under the rules below — we have evidence the simulator is worth investing in for the full experiment. If no, we need better ideas, not endless tweaking on the same data.

---

## When we declare “the simulator works”

**The simulator works only if both sealed exam precincts (B and C) pass, with all guards in this document satisfied.**

That is the proof bar. Practice precincts can look good; they do not count. A single lucky exam run does not count. Passing after the geography-masking probe shows memorization does not count.

| Outcome | Meaning |
|--------|---------|
| B and C pass (two consecutive passing runs each, same frozen personas) + masking probe OK | **Passed** — simulator validated for this backtest |
| B and C fail after one legitimate retake | **Failed** — stop tuning loops; rethink approach |
| Masking probe shows collapse | **Invalid** — “pass” was likely memory, not simulation |
| Infrastructure bug / disqualified run | **Disqualified** — may use reserve sealed pair (see retake rule) |

---

## The closed-book exam (precincts B and C)

**Closed-book** means: two precincts are chosen and **sealed** before any simulation results exist. While you tune on practice precincts, you **never look at B or C’s scores**. They are the final exam.

Why this matters: if you tune until B and C look good, you are not testing the simulator — you are **fitting to those two precincts**. In statistics this is **overfitting**: the model memorizes the homework, not the subject.

**Analogy:** practice problems vs. two exam questions you cannot see until exam day. You only get a real grade if the exam questions were unseen during study.

**Requirement:** B and C must pass before the experiment counts as passed. There is no “we’re close enough on practice” shortcut.

---

## Practice precincts vs. sealed precincts

- **Practice precincts:** used for development — prompt changes, calibration, debugging. Scores here inform decisions.
- **Sealed precincts:** locked away upfront. Scores stay hidden until the formal exam.

For this rehearsal we seal **six** precincts total (three pairs), not only B and C:

| Pair | Role |
|------|------|
| Pair 1 (B, C) | **Exam** — first closed-book attempt |
| Pair 2 | **One legitimate retake** if pair 1 fails |
| Pair 3 | **Reserve** — only for disqualified runs (outage, bug), not for a normal fail |

All six are sealed **before** the first practice run. Random selection and the list are written in the pre-registration log.

---

## The memory problem (exam cheating by the AI)

Large language models are trained on huge swaths of the internet. **Wake County 2020 election results are on the web** (news, Wikipedia, government sites). The model may have “read” real results — including for precincts B and C — during training.

So the model could **recite** plausible numbers instead of **simulating** voters. The closed-book exam alone does not detect that; it only prevents *you* from cheating by tuning on B and C. The model might still cheat from training memory.

### What switching to an open-source model does **not** do

Open-weight models (Qwen, Llama, Mistral, etc.) are trained on largely the same web data. **Swapping models does not make the AI forget 2020.** Research on data contamination shows election facts appear in training corpora and inflate benchmark scores.

### What the open-source swap **does** do (still worth doing)

- **Reproducibility:** pinned model version = same “instrument” every run.
- **No silent API updates** mid-experiment.
- **Lower cost** at our scale (~$1–9 per full pass on serverless APIs).
- **Auditability:** we can point to an exact model string in the log.

**Adopted:** use a pinned open model (recommended: **Qwen3-32B** on **DeepInfra**, OpenAI-compatible API) for the dress rehearsal.

### What actually detects memorization: the geography-masking probe

Run **one diagnostic pass** where place names are hidden in prompts — e.g. “Wake County, Precinct 01-07” becomes “County X, Precinct A” — while demographics and persona details stay the same.

| Masking result | Interpretation |
|----------------|----------------|
| Accuracy **holds up** | Good evidence results come from simulation (not perfect proof — demographics can still hint at place) |
| Accuracy **collapses** | Strong evidence the model was matching memorized geography, not simulating |

Cost: roughly one extra simulation pass (a few dollars). **Adopted:** run the masking probe before declaring any exam passed. If it fails, the exam pass is invalid regardless of B and C scores.

**Do both:** open model for reproducibility and cost; masking probe for cheat detection. If only one, prioritize the probe for detecting fake passes.

---

## Retake rule (burned holdouts)

If the exam fails and you go back to tweaking, **B and C are no longer unseen** — you saw their scores. Re-using them as “exam” after tuning invalidates the test.

**Adopted rule (from holdout-reuse research — small holdouts tolerate very few peeks):**

1. Seal six precincts upfront (three pairs).
2. **Failed exam burns that pair permanently** — it becomes practice data forever.
3. **Exactly one legitimate retake** (pair 2). Two exam attempts is already a meaningful luck subsidy.
4. If pair 2 also fails → experiment **failed**; do not keep tweaking toward a third exam on burned data.
5. Pair 3 is **only** for **disqualified** runs (provider outage, code bug, contamination found before accepting results). A disqualified run does not burn a pair; a legitimate fail does.

**Pass/fail threshold** (e.g. simulated margin within X points of actual in both precincts) must be written **before the first exam** and not changed afterward.

---

## Luck guards (±3 points is normal noise)

With ~300 synthetic voters per precinct, scores naturally wobble run to run — often **±3 percentage points** — from randomness in persona generation and model sampling. A loop that re-runs until something passes will eventually pass by luck.

**Adopted guards:**

1. **Freeze the 300 personas per precinct** once generated. Store a version hash. Any persona change needs a logged reason and resets calibration claims. Prevents “re-roll voters until one set passes.”
2. **Report variance in practice** — run each configuration 3–5 times with different random seeds; report mean and range. Exam-ready only if the **worst** practice run clears the bar, not the best.
3. **Two-of-two replication on the exam** — pass requires two consecutive passing runs on the sealed precincts: same frozen personas, **fresh random seed** for the second run. Borderline pass then fail = fail. Cuts fluke pass rate sharply (e.g. 10% per run → ~1% for two independent passes).
4. **Pre-register** threshold, seeds, persona hash, model version, retake rule in one short document before the first exam.
5. **Log every run** — seed, model version, persona hash, timestamp, result — including failures.

---

## Pre-registration (write the rules before you look)

**Pre-registration** means writing down pass criteria, sealed precinct IDs, retake policy, and luck guards **before** any exam scores exist. It stops quiet goalpost-moving after disappointing results.

Minimum pre-registration checklist:

- [ ] List of six sealed precinct IDs (three pairs) and exam pair assignment
- [ ] Pass threshold (numeric definition per precinct or aggregate)
- [ ] Pinned model ID string (e.g. `Qwen/Qwen3-32B` on DeepInfra)
- [ ] Persona freeze policy and hash storage location
- [ ] Masking probe protocol (when run, what “collapse” means)
- [ ] Retake and disqualification definitions
- [ ] Replication rule (two consecutive passes)

One page is enough. Store it in `docs/experiment/` and reference it in every run log.

---

## Minimal data-foundation pattern (adopted: build minimal version now)

**Problem:** “Margin vs. actual” must be defined once, consistently, everywhere results are compared.

**Minimal pattern for this pipeline:**

1. **Metric definitions as database views** in Supabase (or SQL files next to the backend) — e.g. `dress_rehearsal_precinct_margin` joining simulation outputs to 2020 actuals for Wake County.
2. **A short doc file next to the code** explaining each metric in plain language (what is measured, units, pass threshold link).
3. **Run logs** reference view outputs, not hand-calculated spreadsheets.

This is not a full analytics platform — just enough that pass/fail is computed the same way in the CLI, API, and final report. See the execution plan for the first view to create.

---

## Summary decision log

| Topic | Decision |
|-------|----------|
| Proof bar | B and C (pair 1) must pass; practice alone insufficient |
| Memory | Open model does not fix memorization; masking probe required |
| Model | Qwen3-32B on DeepInfra (pinned version string) |
| Sealed pool | 6 precincts upfront (3 pairs) |
| Retakes | 1 legitimate retake max; pair 3 for disqualification only |
| Luck | Frozen personas, variance reporting, two-of-two exam replication |
| Data foundation | Minimal views + doc now |

**Next document:** `2026-06-12-001-feat-dress-rehearsal-backtest-plan.md` — step-by-step execution order.
