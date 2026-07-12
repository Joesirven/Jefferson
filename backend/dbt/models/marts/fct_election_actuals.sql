-- Analytic copy of dress-rehearsal margin logic for warehouse exploration.
-- Live pass/fail during runs uses Postgres view dress_rehearsal_precinct_margin (sql/002).

select
    precinct_id,
    county,
    state,
    election_year,
    actual_margin,
    dem_votes,
    rep_votes,
    total_votes
from {{ ref('stg_election_precinct_results') }}
