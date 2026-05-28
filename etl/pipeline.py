"""End-to-end ETL pipeline driver.

    python -m etl --input data/raw --db data/processed/zomboid.db

or as a library::

    from etl.pipeline import run
    totals = run(Path("data/raw"), Path("data/processed/zomboid.db"))
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from etl import extract, load, transform

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA = REPO_ROOT / "db" / "schema.sql"

DATASET_TO_TABLE: dict[str, str] = {
    "player_stats": "player_stats",
    "zombie_log": "zombie_sightings",
    "noise_events": "noise_events",
    "inventory_snapshot": "inventory_snapshots",
}


def run(input_dir: Path, db_path: Path, schema_sql: Path = DEFAULT_SCHEMA) -> dict[str, int]:
    engine = load.init_db(db_path, schema_sql)
    totals: dict[str, int] = {t: 0 for t in DATASET_TO_TABLE.values()}
    for raw, df in extract.stream(input_dir):
        table = DATASET_TO_TABLE[raw.dataset]
        clean = transform.transform(raw.dataset, df)
        totals[table] += load.load(engine, table, clean)
    return totals


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Project Zomboid ETL pipeline")
    p.add_argument("--input", type=Path, default=REPO_ROOT / "data" / "raw")
    p.add_argument("--db", type=Path, default=REPO_ROOT / "data" / "processed" / "zomboid.db")
    p.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    p.add_argument("--verbose", "-v", action="store_true")
    args = p.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )

    totals = run(args.input, args.db, args.schema)
    for table, n in totals.items():
        log.info("table %-20s rows loaded: %d", table, n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
