-- Core operational schema for Jefferson (Postgres on ba-sing-se).
-- Apply before 001/002 via: uv run python scripts/apply_sql.py

CREATE TABLE IF NOT EXISTS personas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    race TEXT NOT NULL,
    education TEXT NOT NULL,
    income_bracket TEXT NOT NULL,
    employment_status TEXT NOT NULL,
    marital_status TEXT NOT NULL,
    precinct_id TEXT NOT NULL,
    census_block_group TEXT,
    county TEXT NOT NULL,
    neighborhood TEXT,
    party_id TEXT NOT NULL,
    ideology TEXT NOT NULL,
    vote_history JSONB,
    top_issues TEXT[],
    issue_positions JSONB,
    news_sources TEXT[],
    source_voter_id TEXT,
    socrates_prior BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_personas_precinct ON personas (precinct_id);
CREATE INDEX IF NOT EXISTS idx_personas_county ON personas (county);

CREATE TABLE IF NOT EXISTS simulations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id TEXT UNIQUE NOT NULL,
    results JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'running',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_simulations_created ON simulations (created_at DESC);

CREATE TABLE IF NOT EXISTS survey_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    age_group TEXT,
    education TEXT,
    gender TEXT,
    race TEXT,
    income TEXT,
    party_id TEXT,
    ideology TEXT,
    vote_history JSONB,
    issue_positions JSONB,
    top_issues TEXT[],
    news_sources TEXT[],
    raw_data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS news_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    url TEXT UNIQUE,
    summary TEXT,
    content TEXT,
    source TEXT,
    county TEXT NOT NULL,
    published_at TIMESTAMPTZ,
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_county_date ON news_articles (county, published_at DESC);
