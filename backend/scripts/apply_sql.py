#!/usr/bin/env python3
"""Apply SQL migration scripts in order (000, 001, 002, ...)."""

from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path

import asyncpg
from dotenv import load_dotenv

load_dotenv()

SQL_DIR = Path(__file__).resolve().parent.parent / "sql"


async def apply_sql(database_url: str, dry_run: bool = False) -> None:
    files = sorted(SQL_DIR.glob("*.sql"))
    if not files:
        raise FileNotFoundError(f"No SQL files in {SQL_DIR}")

    if dry_run:
        for path in files:
            print(f"Would apply: {path.name}")
        return

    conn = await asyncpg.connect(database_url)
    try:
        for path in files:
            sql = path.read_text(encoding="utf-8")
            print(f"Applying {path.name}...")
            await conn.execute(sql)
            print(f"  OK")
    finally:
        await conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL"),
        help="Postgres URL (default: DATABASE_URL env)",
    )
    args = parser.parse_args()

    if not args.database_url:
        raise ValueError("Set DATABASE_URL or pass --database-url")

    asyncio.run(apply_sql(args.database_url, dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
