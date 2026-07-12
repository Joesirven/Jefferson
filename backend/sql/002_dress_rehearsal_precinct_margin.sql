-- Dress-rehearsal margin view: simulated vs 2020 actual presidential margin.
-- Requires election_precinct_results and simulations tables.
-- Pass threshold defaults to 5 points; override with DRESS_REHEARSAL_MARGIN_THRESHOLD env
-- when querying, or change the constant below before the exam.

CREATE OR REPLACE VIEW dress_rehearsal_precinct_margin AS
WITH simulation_margins AS (
    SELECT
        s.simulation_id,
        s.created_at AS simulation_created_at,
        precinct_key AS precinct_id,
        -- Extract Democratic share from presidential choice question counts.
        -- Expects results[precinct_id].questions[q1].results.data with
        -- keys like "DEMOCRATIC CANDIDATE" / "REPUBLICAN CANDIDATE".
        (
            COALESCE(
                (
                    SELECT SUM((value)::int)
                    FROM jsonb_each_text(
                        COALESCE(
                            s.results -> precinct_key -> 'questions' -> 'q1' -> 'results' -> 'data',
                            '{}'::jsonb
                        )
                    ) AS t(key, value)
                    WHERE upper(key) LIKE '%DEMOCRAT%'
                ),
                0
            )::float
            /
            NULLIF(
                (
                    SELECT SUM((value)::int)
                    FROM jsonb_each_text(
                        COALESCE(
                            s.results -> precinct_key -> 'questions' -> 'q1' -> 'results' -> 'data',
                            '{}'::jsonb
                        )
                    ) AS t(key, value)
                ),
                0
            )
            * 100.0
            - 50.0
        ) AS simulated_margin,
        (
            SELECT SUM((value)::int)
            FROM jsonb_each_text(
                COALESCE(
                    s.results -> precinct_key -> 'questions' -> 'q1' -> 'results' -> 'data',
                    '{}'::jsonb
                )
            ) AS t(key, value)
        ) AS simulated_response_count
    FROM simulations s
    CROSS JOIN LATERAL jsonb_object_keys(s.results) AS precinct_key
    WHERE s.status = 'completed'
)
SELECT
    sm.simulation_id,
    sm.precinct_id,
    e.county,
    e.state,
    e.election_year,
    sm.simulated_margin,
    CASE
        WHEN e.total_votes > 0 THEN
            ((e.dem_votes::float / e.total_votes) * 100.0)
            - ((e.rep_votes::float / e.total_votes) * 100.0)
        ELSE NULL
    END AS actual_margin,
    sm.simulated_margin
    - CASE
        WHEN e.total_votes > 0 THEN
            ((e.dem_votes::float / e.total_votes) * 100.0)
            - ((e.rep_votes::float / e.total_votes) * 100.0)
        ELSE NULL
    END AS margin_delta,
    ABS(
        sm.simulated_margin
        - CASE
            WHEN e.total_votes > 0 THEN
                ((e.dem_votes::float / e.total_votes) * 100.0)
                - ((e.rep_votes::float / e.total_votes) * 100.0)
            ELSE NULL
        END
    ) <= 5.0 AS within_threshold,
    sm.simulated_response_count,
    e.dem_votes,
    e.rep_votes,
    e.total_votes AS actual_total_votes,
    sm.simulation_created_at
FROM simulation_margins sm
JOIN election_precinct_results e
    ON e.precinct_id = sm.precinct_id
    AND e.county = 'Wake'
    AND e.state = 'NC'
    AND e.election_year = 2020
WHERE sm.simulated_margin IS NOT NULL;

COMMENT ON VIEW dress_rehearsal_precinct_margin IS
    'Per-precinct simulated vs 2020 actual presidential margin (Dem share minus Rep share, percentage points). within_threshold uses 5-point default from pre-registration.';
