from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy.engine import Engine

from etl import load, pipeline

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = Path(__file__).resolve().parent / "fixtures"
SCHEMA = REPO_ROOT / "db" / "schema.sql"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES


@pytest.fixture()
def warehouse(tmp_path: Path) -> Engine:
    return load.init_db(tmp_path / "zomboid.db", SCHEMA)


@pytest.fixture()
def loaded_warehouse(tmp_path: Path) -> tuple[Engine, dict[str, int]]:
    db_path = tmp_path / "zomboid.db"
    totals = pipeline.run(FIXTURES, db_path, SCHEMA)
    engine = load.init_db(db_path, SCHEMA)
    return engine, totals


@pytest.fixture()
def player_stats_df(fixtures_dir: Path) -> pd.DataFrame:
    return pd.read_csv(fixtures_dir / "player_stats_session_demo.csv")
