# Warehouse schema

SQLite warehouse used by the ETL pipeline. Spec lives in `schema.sql` and is
the single source of truth — `etl.load.init_db` reads it directly to
bootstrap a fresh database.

## Tables

| Table | Source | Grain |
|-------|--------|-------|
| `player_stats` | `DataDumper/PlayerStatsLogger.lua` | one row per 2 in-game hours |
| `zombie_sightings` | `DataDumper/ZombieLogger.lua` | one row per zombie per 6 in-game hours |
| `noise_events` | `DataDumper/NoiseLogger.lua` | event-driven (`Events.OnNoise`) |
| `inventory_snapshots` | `DataDumper/InventoryLogger.lua` | one row per stack per 2 in-game hours |
| `nutrition_plan` | optimizer output | one row per (session, day, item) |

## Joining

- All tables carry `(session_id, world_age_hours)` so survival timelines are
  reproducible across datasets.
- `noise_events` is meant to be joined against `zombie_sightings` over a
  forward window to study how zombies migrate after gunshots/explosions.

## Why SQLite, not Postgres

The pipeline is single-writer (one game session = one Lua mod) and the data
volume is small (millions of rows at most for a long campaign). SQLite is
local, file-based, zero-ops, and good enough for the portfolio. The
SQLAlchemy layer in `etl/load.py` would swap to Postgres by changing the
connection URL.
