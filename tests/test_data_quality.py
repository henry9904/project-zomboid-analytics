"""Data-quality gates. These run in CI and block any change that lets bad
rows slip through the pipeline.

Think of this file as the cheap version of Great Expectations — same idea,
just pytest + pandas."""
from __future__ import annotations

import pandas as pd
import pytest
from sqlalchemy import text

# Knox Country (Muldraugh / West Point / Riverside) all fit inside this box.
MAP_MIN, MAP_MAX = 0.0, 15000.0
# Plausible body weight bounds (kg) per PZ nutrition system.
WEIGHT_MIN, WEIGHT_MAX = 30.0, 200.0


def _read(engine, table: str) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(text(f"SELECT * FROM {table}"), conn)


def test_pipeline_loaded_all_tables(loaded_warehouse):
    _, totals = loaded_warehouse
    for table, n in totals.items():
        assert n > 0, f"{table} loaded 0 rows from fixtures"


def test_player_stats_weight_in_human_range(loaded_warehouse):
    engine, _ = loaded_warehouse
    df = _read(engine, "player_stats")
    oob = df.loc[~df["weight"].between(WEIGHT_MIN, WEIGHT_MAX)]
    assert oob.empty, f"weight outside [{WEIGHT_MIN}, {WEIGHT_MAX}]:\n{oob}"


def test_player_stats_no_negative_metrics(loaded_warehouse):
    engine, _ = loaded_warehouse
    df = _read(engine, "player_stats")
    for col in ("calories", "carbs", "protein", "fat", "world_age_hours"):
        assert (df[col] >= 0).all(), f"{col} has negatives"


@pytest.mark.parametrize(
    ("table", "xcol", "ycol"),
    [
        ("player_stats", "x", "y"),
        ("zombie_sightings", "zx", "zy"),
        ("noise_events", "source_x", "source_y"),
    ],
)
def test_coords_within_map(loaded_warehouse, table, xcol, ycol):
    engine, _ = loaded_warehouse
    df = _read(engine, table)
    if df.empty:
        pytest.skip(f"{table} empty")
    assert df[xcol].between(MAP_MIN, MAP_MAX).all(), f"{table}.{xcol} OOB"
    assert df[ycol].between(MAP_MIN, MAP_MAX).all(), f"{table}.{ycol} OOB"


def test_player_stats_normalized_bounds(loaded_warehouse):
    engine, _ = loaded_warehouse
    df = _read(engine, "player_stats")
    for col in ("hunger", "thirst", "fatigue", "stress", "panic", "boredom"):
        assert df[col].between(0.0, 1.0).all(), f"{col} outside [0, 1]"


def test_no_duplicate_player_stats_pk(loaded_warehouse):
    engine, _ = loaded_warehouse
    df = _read(engine, "player_stats")
    dup = df.duplicated(subset=["session_id", "world_age_hours"])
    assert not dup.any(), f"duplicate PK rows:\n{df[dup]}"


def test_world_age_monotonic_per_session(loaded_warehouse):
    engine, _ = loaded_warehouse
    df = _read(engine, "player_stats")
    for sid, g in df.groupby("session_id"):
        ages = g["world_age_hours"].to_numpy()
        assert (ages[1:] >= ages[:-1]).all(), f"session {sid} non-monotonic world_age_hours"
