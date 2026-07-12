-- Election actuals from warehouse Parquet (sync via scripts/sync_warehouse.py)

select
    precinct_id,
    county,
    state,
    election_year,
    dem_votes,
    rep_votes,
    coalesce(other_votes, 0) as other_votes,
    dem_votes + rep_votes + coalesce(other_votes, 0) as total_votes,
    case
        when dem_votes + rep_votes + coalesce(other_votes, 0) > 0 then
            (dem_votes::double / (dem_votes + rep_votes + coalesce(other_votes, 0)) * 100.0)
            - (rep_votes::double / (dem_votes + rep_votes + coalesce(other_votes, 0)) * 100.0)
        else null
    end as actual_margin
from read_parquet('../data/warehouse/election/wake_county_2020_precincts.parquet')
