-- Project Zomboid analytics warehouse (SQLite dialect).
-- All tables share `session_id` (derived from Lua-mod CSV filename) and
-- `world_age_hours` (cumulative in-game time) so they join cleanly.

CREATE TABLE IF NOT EXISTS player_stats (
    session_id      TEXT    NOT NULL,
    world_age_hours REAL    NOT NULL,
    day             INTEGER NOT NULL,
    hour            REAL    NOT NULL,
    x               REAL    NOT NULL,
    y               REAL    NOT NULL,
    z               INTEGER NOT NULL,
    hunger          REAL    NOT NULL,
    thirst          REAL    NOT NULL,
    fatigue         REAL    NOT NULL,
    stress          REAL    NOT NULL,
    panic           REAL    NOT NULL,
    boredom         REAL    NOT NULL,
    calories        REAL    NOT NULL,
    weight          REAL    NOT NULL,
    carbs           REAL    NOT NULL,
    protein         REAL    NOT NULL,
    fat             REAL    NOT NULL,
    PRIMARY KEY (session_id, world_age_hours)
);

CREATE INDEX IF NOT EXISTS idx_player_stats_session ON player_stats(session_id);
CREATE INDEX IF NOT EXISTS idx_player_stats_age     ON player_stats(world_age_hours);

CREATE TABLE IF NOT EXISTS zombie_sightings (
    session_id      TEXT    NOT NULL,
    world_age_hours REAL    NOT NULL,
    zx              REAL    NOT NULL,
    zy              REAL    NOT NULL,
    zz              INTEGER NOT NULL,
    state           TEXT
);

CREATE INDEX IF NOT EXISTS idx_zombie_sightings_session ON zombie_sightings(session_id);
CREATE INDEX IF NOT EXISTS idx_zombie_sightings_age     ON zombie_sightings(world_age_hours);

CREATE TABLE IF NOT EXISTS noise_events (
    session_id      TEXT NOT NULL,
    world_age_hours REAL NOT NULL,
    source_x        REAL NOT NULL,
    source_y        REAL NOT NULL,
    intensity       REAL NOT NULL,
    noise_type      TEXT
);

CREATE INDEX IF NOT EXISTS idx_noise_events_session ON noise_events(session_id);

CREATE TABLE IF NOT EXISTS inventory_snapshots (
    session_id          TEXT    NOT NULL,
    world_age_hours     REAL    NOT NULL,
    item_type           TEXT    NOT NULL,
    count               INTEGER NOT NULL,
    calories_per_unit   REAL,
    carbs_per_unit      REAL,
    protein_per_unit    REAL,
    fat_per_unit        REAL
);

CREATE INDEX IF NOT EXISTS idx_inventory_session ON inventory_snapshots(session_id);

-- Output of the Phase 1 nutrition optimizer.
CREATE TABLE IF NOT EXISTS nutrition_plan (
    session_id      TEXT    NOT NULL,
    day_idx         INTEGER NOT NULL,
    item_type       TEXT    NOT NULL,
    servings        REAL    NOT NULL,
    total_calories  REAL    NOT NULL,
    PRIMARY KEY (session_id, day_idx, item_type)
);
