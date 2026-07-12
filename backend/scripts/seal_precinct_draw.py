#!/usr/bin/env python3
"""Draw six sealed precincts from Wake County 2020 inventory and update prereg log."""

from __future__ import annotations

import argparse
import csv
import random
import re
from datetime import UTC, datetime
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_ROOT.parent
DEFAULT_CSV = BACKEND_ROOT / "data" / "election" / "wake_county_2020_precincts.csv"
DEFAULT_PREREG = REPO_ROOT / "docs" / "experiment" / "2026-06-12-preregistration-log.md"
DEFAULT_SEED = 20260612


def load_precinct_ids(csv_path: Path) -> list[str]:
    with csv_path.open(newline="", encoding="utf-8") as handle:
        return sorted(row["precinct_id"].strip() for row in csv.DictReader(handle))


def draw_pairs(precinct_ids: list[str], seed: int) -> list[tuple[str, str]]:
    rng = random.Random(seed)
    drawn = rng.sample(precinct_ids, 6)
    return [(drawn[0], drawn[1]), (drawn[2], drawn[3]), (drawn[4], drawn[5])]


def update_prereg_log(
    prereg_path: Path,
    seed: int,
    pairs: list[tuple[str, str]],
    *,
    dry_run: bool,
) -> None:
    text = prereg_path.read_text(encoding="utf-8")
    if "PLACEHOLDER_EXAM_B" not in text:
        if dry_run:
            print("Pre-registration log already sealed — dry run only shows draw")
            return
        raise ValueError("Pre-registration log already sealed — refusing to re-draw")

    timestamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    (exam_b, exam_c), (retake_1, retake_2), (disq_1, disq_2) = pairs

    replacements = {
        "PLACEHOLDER_EXAM_B": exam_b,
        "PLACEHOLDER_EXAM_C": exam_c,
        "PLACEHOLDER_RETAKE_1": retake_1,
        "PLACEHOLDER_RETAKE_2": retake_2,
        "PLACEHOLDER_DISQ_1": disq_1,
        "PLACEHOLDER_DISQ_2": disq_2,
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"\*\*Random draw seed:\*\* `PLACEHOLDER_DRAW_SEED`[^\n]*",
        f"**Random draw seed:** `{seed}` (drawn {timestamp})",
        text,
        count=1,
    )

    text = re.sub(
        r"- \[ \] Six sealed IDs filled \(no placeholders\)",
        "- [x] Six sealed IDs filled (no placeholders)",
        text,
        count=1,
    )

    if dry_run:
        print("Dry run — prereg log not written")
        print(text[text.index("## Sealed precinct pool"): text.index("## Persona freeze policy")])
        return

    prereg_path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--prereg", type=Path, default=DEFAULT_PREREG)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    precinct_ids = load_precinct_ids(args.csv)
    if len(precinct_ids) < 6:
        raise ValueError(f"Need at least 6 precincts, found {len(precinct_ids)}")

    pairs = draw_pairs(precinct_ids, args.seed)
    print(f"Inventory: {len(precinct_ids)} precincts from {args.csv}")
    print(f"Seed: {args.seed}")
    for idx, (a, b) in enumerate(pairs, start=1):
        print(f"  Pair {idx}: {a}, {b}")

    update_prereg_log(args.prereg, args.seed, pairs, dry_run=args.dry_run)
    if not args.dry_run:
        print(f"Updated {args.prereg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
