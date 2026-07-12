-- 2020 precinct-level presidential election results.
-- Run via: uv run python scripts/apply_sql.py (after 000_core_schema.sql)

CREATE TABLE IF NOT EXISTS election_precinct_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    precinct_id TEXT NOT NULL,
    county TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'NC',
    election_year INTEGER NOT NULL DEFAULT 2020,
    dem_votes INTEGER NOT NULL CHECK (dem_votes >= 0),
    rep_votes INTEGER NOT NULL CHECK (rep_votes >= 0),
    other_votes INTEGER NOT NULL DEFAULT 0 CHECK (other_votes >= 0),
    total_votes INTEGER GENERATED ALWAYS AS (dem_votes + rep_votes + other_votes) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (precinct_id, county, state, election_year)
);

CREATE INDEX IF NOT EXISTS idx_election_precinct_results_lookup
    ON election_precinct_results (county, state, election_year, precinct_id);

COMMENT ON TABLE election_precinct_results IS
    'Official precinct vote totals for dress-rehearsal backtest comparisons.';
