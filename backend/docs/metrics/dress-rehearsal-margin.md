# Dress-rehearsal margin metrics

Plain-language definitions for the `dress_rehearsal_precinct_margin` SQL view (`backend/sql/002_dress_rehearsal_precinct_margin.sql`).

## What is being measured

The dress rehearsal compares **simulated presidential vote share** in a Wake County precinct to **official 2020 general election results** for that same precinct.

Each synthetic voter is polled on a presidential choice question (`q1` in simulation results). We aggregate responses into a two-party margin and compare it to the real margin from `election_precinct_results`.

## Margin definition

All margins are in **percentage points** on a Dem-minus-Rep scale:

```
margin = (dem_share - rep_share) * 100
       = (dem_votes / total - rep_votes / total) * 100
```

Examples:

| Outcome | Margin |
|---------|--------|
| 60% Dem, 40% Rep | +20.0 |
| 48% Dem, 50% Rep | -2.0 |
| Tie | 0.0 |

### `simulated_margin`

Two-party margin from synthetic poll responses in the simulation JSON (`simulations.results`). Uses choice counts whose keys contain `DEMOCRAT` or `REPUBLICAN` (case-insensitive).

### `actual_margin`

Two-party margin from `election_precinct_results` for Wake County, NC, 2020.

### `margin_delta`

```
margin_delta = simulated_margin - actual_margin
```

Positive delta means the simulation leaned more Democratic than reality; negative means more Republican.

### `within_threshold`

Boolean pass flag:

```
within_threshold = ABS(margin_delta) <= threshold
```

Default threshold in the view SQL is **5.0 percentage points**, matching the pre-registration log (`docs/experiment/2026-06-12-preregistration-log.md`). Update the constant in the view SQL before the exam if the pre-registered threshold changes — do not change it after practice ends.

## Data sources

| Object | Location |
|--------|----------|
| Actuals table | `backend/sql/001_election_precinct_results.sql` |
| Seed CSV | `backend/data/election/wake_county_2020_precincts.csv` |
| View | `backend/sql/002_dress_rehearsal_precinct_margin.sql` |
| Simulation output | `simulations.results` JSONB |

## Usage

1. Start Postgres: `docker compose up -d` (in `backend/`).
2. Apply SQL: `uv run python scripts/apply_sql.py` (runs 000, 001, 002 in order).
3. Load Wake County 2020 CSV: `uv run python scripts/ingest_wake_county_2020.py`.
4. Sync warehouse Parquet: `uv run python scripts/sync_warehouse.py`.
5. Run simulations with presidential choice question `q1`.
6. Query the view for pass/fail:

```sql
SELECT precinct_id, simulated_margin, actual_margin, margin_delta, within_threshold
FROM dress_rehearsal_precinct_margin
WHERE simulation_id = '<run_id>';
```

## Related experiment rules

- Exam pass requires **both** sealed precincts `within_threshold` on **two consecutive runs** (same frozen personas, new seed).
- Practice tuning must **not** use sealed precinct scores.
- Masking probe collapse invalidates an exam pass even if thresholds are met.

See `docs/experiment/2026-06-11-experiment-success-determinants-requirements.md`.
