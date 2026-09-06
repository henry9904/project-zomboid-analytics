"""Discover and read raw CSV dumps written by the DataDumper Lua mod.

The Lua mod writes one file per dataset per session, named
``<dataset>_session_<session_id>.csv`` (e.g. ``player_stats_session_42.csv``).
Extract walks the input directory, parses the filename for the dataset and
the session id, and yields ``(RawFile, DataFrame)`` pairs.
"""
from __future__ import annotations

import logging
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

log = logging.getLogger(__name__)

DATASETS: tuple[str, ...] = (
    "player_stats",
    "zombie_log",
    "noise_events",
    "inventory_snapshot",
)


@dataclass(frozen=True)
class RawFile:
    dataset: str
    session_id: str
    path: Path


def discover(raw_dir: Path) -> list[RawFile]:
    files: list[RawFile] = []
    for ds in DATASETS:
        for p in sorted(raw_dir.glob(f"{ds}_session_*.csv")):
            session_id = p.stem.removeprefix(f"{ds}_session_")
            files.append(RawFile(ds, session_id, p))
    log.info("discovered %d raw files under %s", len(files), raw_dir)
    return files


def read(raw: RawFile) -> pd.DataFrame:
    df = pd.read_csv(raw.path)
    if "session_id" not in df.columns:
        df.insert(0, "session_id", raw.session_id)
    return df


def stream(raw_dir: Path) -> Iterator[tuple[RawFile, pd.DataFrame]]:
    for r in discover(raw_dir):
        yield r, read(r)
