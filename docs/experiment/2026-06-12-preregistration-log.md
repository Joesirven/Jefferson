# Dress-rehearsal pre-registration log

**Sealed:** 2026-06-12 (before first practice run)  
**Requirements:** [2026-06-11-experiment-success-determinants-requirements.md](./2026-06-11-experiment-success-determinants-requirements.md)  
**Runbook:** [2026-06-12-001-feat-dress-rehearsal-backtest-plan.md](./2026-06-12-001-feat-dress-rehearsal-backtest-plan.md)

> **Do not edit pass criteria or sealed IDs after the first exam attempt.** Log amendments with date and reason only for infrastructure disqualifications.

---

## Model and provider (pinned)

| Field | Value |
|-------|-------|
| Provider | DeepInfra (OpenAI-compatible API) |
| Base URL | `https://api.deepinfra.com/v1/openai` |
| Model ID | `Qwen/Qwen3-32B` |
| Env | `LLM_PROVIDER=openai_compat` |
| Pinned date | 2026-06-12 |

---

## Pass threshold

| Metric | Definition |
|--------|------------|
| Unit | Percentage points (Dem share − Rep share) |
| Per-precinct pass | `ABS(margin_delta) <= 5.0` |
| Exam pass | Both precincts in the exam pair pass threshold |
| Replication | Two consecutive passing exam runs (same frozen personas, new random seed each run) |

SQL view: `dress_rehearsal_precinct_margin` (`backend/sql/002_dress_rehearsal_precinct_margin.sql`).

---

## Sealed precinct pool (6 precincts, 3 pairs)

**Random draw seed:** `20260612` (drawn 2026-06-12 16:46 UTC)

| Pair | Role | Precinct A | Precinct B | Labels in logs |
|------|------|------------|------------|----------------|
| 1 | **Exam (closed-book)** | `01-08` | `01-12` | B, C |
| 2 | Legitimate retake (one use if pair 1 fails) | `02-01` | `03-05` | — |
| 3 | Disqualification reserve only | `01-02` | `02-05` | — |

**Draw procedure:** inventory Wake County 2020 precincts with actuals loaded → `random.sample` with documented seed → assign pairs as above → record IDs here → do not re-draw.

**Access control:** practice scripts filter `precinct_id NOT IN (sealed list)`. Exam pair results not opened until formal exam phase.

---

## Persona freeze policy

- ~300 synthetic personas per precinct, generated once per precinct.
- Store persona set hash (SHA-256 of sorted persona IDs + key demographic fields) in run metadata.
- **No regeneration** without logged reason; regeneration resets calibration claims for that precinct.
- Exam replication reuses frozen personas; only the poll random seed changes.

---

## Masking probe protocol

| Field | Value |
|-------|-------|
| When | After practice exam-ready gate; **before** accepting any exam pass |
| Method | Replace county/precinct/neighborhood names with generic labels; demographics unchanged |
| Collapse rule | If `ABS(margin_delta)` under masking exceeds unmasked delta by **> 10 percentage points** on the same precinct → probe **fail** |
| Consequence | Exam pass invalid; investigate memorization |

Log as `run_type=masking_probe`.

---

## Retake and disqualification

1. **Pair 1 fail (legitimate):** pair 1 burned permanently; exactly **one** retake on pair 2.
2. **Pair 2 fail:** experiment **failed** — no third exam on burned holdouts.
3. **Disqualified run** (outage, wrong model, code bug before accepting results): may use pair 3; does **not** burn a pair on infrastructure failure alone.

---

## Luck guards (adopted)

- [x] Freeze 300 personas per precinct with version hash
- [x] Report variance: 3–5 seeds in practice; exam-ready when **worst** practice run clears threshold
- [x] Two-of-two replication on exam pair
- [x] Pre-register threshold, model, retake rule (this document)
- [x] Log every run including failures

---

## Run log template

| run_id | run_type | pair | precinct_ids | seed | model_version | persona_hash | masked | status | margin_snapshot |
|--------|----------|------|--------------|------|---------------|--------------|--------|--------|-----------------|
| | practice | — | | | Qwen/Qwen3-32B | | false | | |
| | masking_probe | — | | | Qwen/Qwen3-32B | | true | | |
| | exam | 1 | B, C | S1 | Qwen/Qwen3-32B | | false | | |
| | exam | 1 | B, C | S2 | Qwen/Qwen3-32B | | false | | |

---

## Checklist before first exam

- [x] Six sealed IDs filled (no placeholders)
- [ ] Wake County 2020 actuals loaded (`election_precinct_results`)
- [ ] `llm.py` restored; DeepInfra smoke test passed
- [ ] Margin view deployed in Supabase
- [ ] Practice worst-of-seeds gate met
- [ ] Masking probe passed
