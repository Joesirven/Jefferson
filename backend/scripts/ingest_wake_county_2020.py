#!/usr/bin/env python3
"""Load Wake County 2020 precinct presidential results into Postgres."""

from __future__ import annotations

import argparse
import asyncio
import csv
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CSV = Path(__file__).resolve().parent.parent / "data" / "election" / "wake_county_2020_precincts.csv"


def load_csv(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(
                {
                    "precinct_id": row["precinct_id"].strip(),
                    "county": row.get("county", "Wake").strip(),
                    "state": row.get("state", "NC").strip(),
                    "election_year": int(row.get("election_year", 2020)),
                    "dem_votes": int(row["dem_votes"]),
                    "rep_votes": int(row["rep_votes"]),
                    "other_votes": int(row.get("other_votes", 0)),
                }
            )
    return rows


async def upsert_to_postgres(rows: list[dict], database_url: str) -> int:
    conn = await asyncpg.connect(database_url)
    try:
        count = 0
        for row in rows:
            await conn.execute(
                """
                INSERT INTO election_precinct_results (
                    precinct_id, county, state, election_year,
                    dem_votes, rep_votes, other_votes
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (precinct_id, county, state, election_year) DO UPDATE SET
                    dem_votes = EXCLUDED.dem_votes,
                    rep_votes = EXCLUDED.rep_votes,
                    other_votes = EXCLUDED.other_votes
                """,
                row["precinct_id"],
                row["county"],
                row["state"],
                row["election_year"],
                row["dem_votes"],
                row["rep_votes"],
                row["other_votes"],
            )
            count += 1
        return count
    finally:
        await conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.csv.exists():
        raise FileNotFoundError(f"CSV not found: {args.csv}")

    rows = load_csv(args.csv)
    print(f"Loaded {len(rows)} precinct rows from {args.csv}")

    if args.dry_run:
        print("Dry run — not writing to Postgres")
        for row in rows[:3]:
            print(f"  {row}")
        if len(rows) > 3:
            print(f"  ... and {len(rows) - 3} more")
        return 0

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL must be set")

    count = asyncio.run(upsert_to_postgres(rows, database_url))
    print(f"Upserted {count} rows into election_precinct_results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
