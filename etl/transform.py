"""Per-dataset transforms applied between extract and load.

The ``SCHEMAS`` dict is the single source of truth for what columns each
dataset must carry and what dtype they get stored as. Missing columns cause
a ``TransformError`` (loud, blocks the pipeline). Negative ``world_age_hours``
rows are dropped with a warning — they only occur when the Lua mod logs
before ``getGameTime()`` is fully initialized.
"""
from __future__ import annotations

import logging

import pandas as pd

log = logging.getLogger(__name__)

SCHEMAS: dict[str, dict[str, str]] = {
    "player_stats": {
        "session_id": "string",
        "world_age_hours": "float64",
        "day": "int64",
        "hour": "float64",
        "x": "float64",
        "y": "float64",
        "z": "int64",
        "hunger": "float64",
        "thirst": "float64",
        "fatigue": "float64",
        "stress": "float64",
        "panic": "float64",
        "boredom": "float64",
        "calories": "float64",
        "weight": "float64",
        "carbs": "float64",
        "protein": "float64",
        "fat": "float64",
    },
    "zombie_log": {
        "session_id": "string",
        "world_age_hours": "float64",
        "zx": "float64",
        "zy": "float64",
        "zz": "int64",
        "state": "string",
    },
    "noise_events": {
        "session_id": "string",
        "world_age_hours": "float64",
        "source_x": "float64",
        "source_y": "float64",
        "intensity": "float64",
        "noise_type": "string",
    },
    "inventory_snapshot": {
        "session_id": "string",
        "world_age_hours": "float64",
        "item_type": "string",
        "count": "int64",
        "calories_per_unit": "float64",
        "carbs_per_unit": "float64",
        "protein_per_unit": "float64",
        "fat_per_unit": "float64",
    },
}


class TransformError(Exception):
    """Raised when a dataset cannot be coerced into its declared schema."""


def transform(dataset: str, df: pd.DataFrame) -> pd.DataFrame:
    schema = SCHEMAS.get(dataset)
    if schema is None:
        raise TransformError(f"unknown dataset: {dataset}")

    missing = set(schema) - set(df.columns)
    if missing:
        raise TransformError(f"{dataset}: missing columns {sorted(missing)}")

    out = df[list(schema)].copy()
    for col, dtype in schema.items():
        try:
            out[col] = out[col].astype(dtype)
        except (ValueError, TypeError) as exc:
            raise TransformError(
                f"{dataset}.{col} cast to {dtype} failed: {exc}"
            ) from exc

    if "world_age_hours" in out.columns:
        before = len(out)
        out = out[out["world_age_hours"] >= 0]
        dropped = before - len(out)
        if dropped:
            log.warning(
                "%s: dropped %d rows with negative world_age_hours", dataset, dropped
            )

    out = out.drop_duplicates()
    return out.reset_index(drop=True)
