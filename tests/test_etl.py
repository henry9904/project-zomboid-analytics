from __future__ import annotations

import pandas as pd
import pytest

from etl import transform


def test_transform_rejects_missing_columns():
    df = pd.DataFrame({"session_id": ["a"], "world_age_hours": [1.0]})
    with pytest.raises(transform.TransformError, match="missing columns"):
        transform.transform("player_stats", df)


def test_transform_rejects_unknown_dataset():
    with pytest.raises(transform.TransformError, match="unknown dataset"):
        transform.transform("not_a_real_dataset", pd.DataFrame())


def test_transform_drops_negative_world_age(player_stats_df):
    bad = player_stats_df.copy()
    bad.loc[0, "world_age_hours"] = -5.0
    out = transform.transform("player_stats", bad)
    assert (out["world_age_hours"] >= 0).all()
    assert len(out) == len(player_stats_df) - 1


def test_transform_idempotent(player_stats_df):
    once = transform.transform("player_stats", player_stats_df)
    twice = transform.transform("player_stats", once)
    pd.testing.assert_frame_equal(once, twice)


def test_transform_deduplicates(player_stats_df):
    doubled = pd.concat([player_stats_df, player_stats_df], ignore_index=True)
    out = transform.transform("player_stats", doubled)
    assert len(out) == len(player_stats_df)
