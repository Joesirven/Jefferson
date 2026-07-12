# Dress-rehearsal backtest — execution plan

**Feature:** `001-feat-dress-rehearsal-backtest`  
**Requirements:** `2026-06-11-experiment-success-determinants-requirements.md`  
**Last updated:** 2026-06-12 (rebuilt; research integrated)

This is the **how-to runbook**. Read the requirements doc first for *why* each rule exists.

---

## Scope

| Item | Choice |
|------|--------|
| Geography | Wake County, North Carolina |
| Election | 2020 general (presidential margin at precinct level) |
| Scale | ~300 synthetic voters per precinct |
| Holdout | 6 sealed precincts (3 pairs); exam on pair 1 (B, C) |
| Practice | Remaining Wake precincts not in the sealed pool |

**Success** = pair 1 exam passes twice consecutively (frozen personas, new seed), masking probe OK, all logs complete. See requirements for fail / invalid / disqualified paths.

---

## Phase 0 — Prerequisites

### 0.1 Restore `llm.py` before any model work

**Status check (2026-06-12):** `backend/src/tasks/llm.py` is **broken**. The `GLMClient` class declaration is missing — its constructor code is orphaned inside the abstract `LLMClient` base class. `get_llm_client()` still references `GLMClient`, so the default `glm` provider would crash at runtime.

The intact version is **`backend/src/tasks/llm.py.backup`**, which contains a complete `GLMClient` implementation.

**Action before integration:** restore from backup (copy backup → `llm.py`, then add the new provider on top). Do not run dress-rehearsal simulations against the current broken file.

### 0.2 Pin open model on DeepInfra

1. Create DeepInfra account; obtain API key.
2. Choose exact model string — recommended: **`Qwen/Qwen3-32B`** (runner-up: Mistral Small 3.2 24B for format compliance).
3. Record in pre-registration log: model string, API endpoint, date pinned.
4. Environment variables (after integration):

```bash
LLM_PROVIDER=openai_compat   # new factory branch
OPENAI_API_KEY=<deepinfra_key>
OPENAI_BASE_URL=https://api.deepinfra.com/v1/openai
OPENAI_MODEL=Qwen/Qwen3-32B
```

### 0.3 Integrate OpenAI-compatible client (~half day)

**File:** `backend/src/tasks/llm.py` (after restore from backup)

1. Add `OpenAICompatClient(LLMClient)` — ~30 lines using the `openai` Python SDK with custom `base_url`.
2. Implement `async def generate(prompt, **kwargs)` matching existing callers.
3. Add factory branch for `openai_compat` (or `deepinfra`) in `get_llm_client()`.
4. Smoke test: 10 personas, one poll question, eyeball responses for format and persona consistency.

**No changes required** in `simulation.py`, `cli.py`, or `api/main.py` — all use `get_llm_client()`.

### 0.4 Minimal data foundation

1. **SQL view** (Supabase SQL editor or migration file next to backend):

   - Input: simulation results + 2020 actual precinct totals for Wake County.
   - Output per precinct: `simulated_margin`, `actual_margin`, `margin_delta`, `within_threshold` (boolean).

2. **Doc:** `backend/docs/metrics/dress-rehearsal-margin.md` — plain-language definition of margin, delta, and how `within_threshold` maps to the pre-registered pass threshold.

3. CLI/report queries use the view; no ad-hoc margin math in scripts.

### 0.5 Pre-registration packet

Create `docs/experiment/2026-06-12-preregistration-log.md` (or section in run journal) with:

- Six sealed precinct IDs (random draw documented)
- Pass threshold (e.g. `|margin_delta| <= 5` points per precinct — **set your number before practice ends**)
- Persona freeze policy
- Model string and provider
- Masking collapse criterion (e.g. delta widens by >10 points under masking → fail probe)

---

## Precinct sealing protocol

Do this **once**, before any simulation that could inform tuning.

1. **Inventory** all Wake County 2020 precincts with actual results loaded.
2. **Random draw** six precincts into three pairs (document seed used for draw).
3. **Assign roles:**
   - Pair 1 → Exam (B, C labels in logs)
   - Pair 2 → Legitimate retake reserve
   - Pair 3 → Disqualification reserve only
4. **Write IDs to pre-registration log.** No re-draw after practice starts.
5. **Access control (process):** exam precinct results are not opened until the formal exam phase. Practice scripts filter `precinct_id NOT IN (sealed list)`.

Remaining precincts are practice-eligible.

---

## Phase 1 — Persona freeze

For each precinct in the run (practice + sealed):

1. Generate ~300 personas (existing ingestion / persona pipeline).
2. Save to Supabase `personas` table with `precinct_id`.
3. Compute and store **persona set hash** (e.g. SHA-256 of sorted persona IDs + key fields) in run metadata.
4. **Do not regenerate** personas for a precinct without logging reason and resetting “calibrated” status.

---

## Phase 2 — Practice runs

**Goal:** tune prompts and pipeline until practice precincts are stable — without touching sealed scores.

| Step | Action |
|------|--------|
| 1 | Run simulation on practice precincts only |
| 2 | For each candidate configuration, run **3–5 seeds** |
| 3 | Query margin view; record mean, min, max delta per precinct |
| 4 | **Exam-ready gate:** worst practice run across seeds must clear threshold (not best) |
| 5 | Log every run: `run_id`, seed, model version, persona hash, precinct set, timestamps, view outputs |

Iterate until exam-ready gate met or you abandon the configuration.

**Do not** open pair 1 results during this phase.

---

## Phase 3 — Geography-masking probe

Run **before** accepting any exam pass.

1. Select practice precincts (or a dedicated diagnostic subset — not required to be B/C).
2. Clone prompts with **all geography masked** (county, precinct names, neighborhood → generic labels). Demographics and persona text unchanged.
3. Run one full pass (frozen personas, documented seed).
4. Compare `margin_delta` vs. unmasked runs on the same precincts.

| Result | Action |
|--------|--------|
| Deltas similar (within pre-registered collapse rule) | Probe **pass** — proceed to exam |
| Deltas collapse | Probe **fail** — exam invalid; investigate memorization; do not declare success |

Log probe as its own `run_type=masking_probe` in run metadata.

---

## Phase 4 — Closed-book exam (pair 1)

**Preconditions:** practice exam-ready gate met; masking probe pass; pre-registration complete; `llm.py` restored and smoke-tested.

1. Run simulation on **pair 1 only** (B, C) — frozen personas, seed `S1`.
2. Query margin view; check `within_threshold` for both precincts.
3. **Do not tune** based on these results until replication complete.

If both precincts pass threshold → proceed to Phase 5.  
If either fails → pair 1 **burned**; one retake on pair 2 (Phase 4b).  
If pair 2 also fails → experiment **failed**.

### Phase 4b — Legitimate retake (pair 2)

Same protocol as Phase 4 on pair 2 precincts. Pair 1 never returns to exam status.

### Phase 4c — Disqualified run (pair 3 only)

Use pair 3 only when run is void (outage, bug, wrong model version). Document disqualification reason. Pair 3 does **not** apply to a normal fail on threshold.

---

## Phase 5 — Exam replication (two-of-two)

After a passing exam run (seed `S1`):

1. Re-run **same pair, same frozen personas**, new seed `S2`.
2. Both precincts must pass threshold again.
3. If run 1 pass + run 2 fail → **fail** (do not cherry-pick run 1).

Only after **two consecutive passes** + masking probe pass → dress rehearsal **passed**.

---

## Run order summary

```
Prerequisites (restore llm.py, model setup, views, pre-register)
    → Persona freeze (all precincts)
    → Practice loops (practice precincts only, multi-seed variance)
    → Masking probe
    → Exam pair 1 (seed S1)
    → Exam pair 1 replication (seed S2)
    → [If fail] Exam pair 2 + replication
    → [If disqualified only] Exam pair 3 + replication
```

---

## Logging requirements

Every run record should include:

| Field | Example |
|-------|---------|
| `run_id` | UUID |
| `run_type` | `practice` / `exam` / `masking_probe` / `retake` |
| `precinct_ids` | list |
| `pair_number` | 1, 2, or 3 for sealed runs |
| `random_seed` | integer |
| `model_version` | `Qwen/Qwen3-32B` |
| `persona_hash` | SHA-256 |
| `masked_geography` | boolean |
| `started_at` / `completed_at` | timestamps |
| `status` | `completed` / `failed` / `disqualified` |
| `margin_view_snapshot` | JSON from dress-rehearsal view |

Store in `simulations` table JSONB or a dedicated `dress_rehearsal_runs` table. **Failures must be logged**, not deleted.

---

## Pass criteria checklist

- [ ] Practice: worst-of-seeds runs meet threshold on practice precincts
- [ ] Masking probe: no collapse under pre-registered rule
- [ ] Exam pair 1: both precincts `within_threshold` on run 1
- [ ] Exam pair 1: both precincts `within_threshold` on run 2 (new seed, same personas)
- [ ] Pre-registration document complete and unchanged
- [ ] All runs logged with seeds and persona hashes
- [ ] `llm.py` was restored from backup before model integration

---

## Cost estimate

Per research estimate for ~12 precincts × 300 voters × 2–3 calls:

- ~10–15M tokens per full pass
- DeepInfra Qwen3-32B: roughly **$1–9 per full pass**
- Full dress rehearsal (practice iterations + probe + exam + replication): typically **under $200**

Self-hosted GPU is not recommended at this volume.

---

## Known blockers / risks

| Blocker | Mitigation |
|---------|------------|
| `llm.py` broken | Restore from `.backup` before any runs |
| Original planning docs not recovered | Rebuilt in `docs/experiment/` from session transcript + research (2026-06-12 recovery: no `~/.ssh/config`; SSH to `ba-sing-se` failed host-key verification; no matches in `~/.claude`) |
| 2020 actuals not loaded for Wake | Complete ingestion before sealing |
| Exam precinct IDs leaked during practice | Process + script filters on sealed list |
| Model API outage during exam | Disqualify run; use pair 3; do not burn pair on outage |

---

## File map

| Path | Purpose |
|------|---------|
| `docs/experiment/2026-06-11-experiment-success-determinants-requirements.md` | Rules and definitions |
| `docs/experiment/2026-06-12-001-feat-dress-rehearsal-backtest-plan.md` | This runbook |
| `docs/experiment/2026-06-12-preregistration-log.md` | To create at seal time |
| `backend/src/tasks/llm.py` | Model integration (restore first) |
| `backend/src/tasks/llm.py.backup` | Known-good GLM client reference |
| `backend/docs/metrics/dress-rehearsal-margin.md` | Metric definitions (to create) |
