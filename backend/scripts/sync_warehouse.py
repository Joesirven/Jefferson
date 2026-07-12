#!/usr/bin/env python3
"""Sync operational data to Parquet files for DuckDB/dbt analytics."""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

import asyncpg
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BACKEND_ROOT = Path(__file__).resolve().parent.parent
WAREHOUSE_DIR = BACKEND_ROOT / "data" / "warehouse"
ELECTION_CSV = BACKEND_ROOT / "data" / "election" / "wake_county_2020_precincts.csv"


def csv_to_parquet() -> Path:
    out_dir = WAREHOUSE_DIR / "election"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "wake_county_2020_precincts.parquet"
    df = pd.read_csv(ELECTION_CSV)
    df.to_parquet(out_path, index=False)
    print(f"Wrote {out_path} ({len(df)} rows)")
    return out_path


async def export_postgres_tables(database_url: str) -> None:
    conn = await asyncpg.connect(database_url)
    try:
        for table in ("election_precinct_results", "simulations"):
            exists = await conn.fetchval(
                "SELECT to_regclass($1)", f"public.{table}"
            )
            if not exists:
                print(f"Skip {table} (not found)")
                continue

            rows = await conn.fetch(f"SELECT * FROM {table}")
            if not rows:
                print(f"Skip {table} (empty)")
                continue

            df = pd.DataFrame([dict(r) for r in rows])
            out_dir = WAREHOUSE_DIR / "postgres"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{table}.parquet"
            df.to_parquet(out_path, index=False)
            print(f"Wrote {out_path} ({len(df)} rows)")
    finally:
        await conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--from-postgres",
        action="store_true",
        help="Export Postgres tables to parquet (requires DATABASE_URL)",
    )
    args = parser.parse_args()

    csv_to_parquet()

    if args.from_postgres:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL must be set for --from-postgres")
        asyncio.run(export_postgres_tables(database_url))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
