"""Warehouse loader.

Thin wrapper over SQLAlchemy + sqlite. ``init_db`` reads ``db/schema.sql``
and executes it idempotently; ``load`` appends a transformed dataframe to
the given table.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

log = logging.getLogger(__name__)


def init_db(db_path: Path, schema_sql: Path) -> Engine:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    ddl = schema_sql.read_text(encoding="utf-8")
    with engine.begin() as conn:
        for stmt in (s.strip() for s in ddl.split(";")):
            if stmt and not stmt.startswith("--"):
                conn.execute(text(stmt))
    return engine


def load(engine: Engine, table: str, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    df.to_sql(table, engine, if_exists="append", index=False)
    log.info("loaded %d rows into %s", len(df), table)
    return len(df)
