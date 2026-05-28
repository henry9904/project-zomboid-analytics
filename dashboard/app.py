"""Streamlit dashboard for the Zomboid analytics warehouse.

Run locally::

    streamlit run dashboard/app.py -- --db data/processed/zomboid.db

The `--` separator is required by Streamlit to pass args through to the script.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--db", type=Path, default=Path("data/processed/zomboid.db"))
    return p.parse_known_args()[0]


@st.cache_data(show_spinner=False)
def load_table(db_path: str, table: str) -> pd.DataFrame:
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.connect() as conn:
        return pd.read_sql(text(f"SELECT * FROM {table}"), conn)


def main() -> None:
    args = parse_args()
    st.set_page_config(page_title="Zomboid Analytics", layout="wide")
    st.title("Project Zomboid — Survival Analytics")
    st.caption(f"warehouse: `{args.db}`")

    if not args.db.exists():
        st.error("Warehouse not found. Run `python -m etl` first.")
        return

    player = load_table(str(args.db), "player_stats")
    zombies = load_table(str(args.db), "zombie_sightings")
    noise = load_table(str(args.db), "noise_events")

    if player.empty:
        st.warning("No player_stats rows. Run a game session with DataDumper.")
        return

    sessions = sorted(player["session_id"].unique().tolist())
    session = st.sidebar.selectbox("Session", sessions)
    p = player[player.session_id == session].sort_values("world_age_hours")
    z = zombies[zombies.session_id == session]

    c1, c2, c3 = st.columns(3)
    c1.metric("Hours survived", f"{p['world_age_hours'].max():.1f}")
    c2.metric(
        "Weight (kg)",
        f"{p['weight'].iloc[-1]:.1f}",
        delta=f"{p['weight'].iloc[-1] - p['weight'].iloc[0]:.1f}",
    )
    c3.metric("Zombie sightings", len(z))

    st.subheader("Calories & weight over time")
    fig = px.line(p, x="world_age_hours", y=["calories", "weight"], markers=True)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Stress / panic / fatigue / boredom")
    fig2 = px.line(p, x="world_age_hours", y=["stress", "panic", "fatigue", "boredom"])
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Zombie sighting density")
    if not z.empty:
        fig3 = px.density_heatmap(z, x="zx", y="zy", nbinsx=40, nbinsy=40)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No zombie sightings for this session.")

    session_noise = noise[noise.session_id == session]
    if not session_noise.empty:
        st.subheader("Noise events")
        st.dataframe(session_noise)


if __name__ == "__main__":
    main()
