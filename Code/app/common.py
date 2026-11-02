"""Shared pieces: data loading, colors, the header. Every page imports this."""

from pathlib import Path

import pandas as pd
import streamlit as st

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
ASSETS = HERE / "assets"

APP_NAME = "Brand Radar"
EURPAC_GRAY, EURPAC_BLUE, EURPAC_RED = "#4A4D54", "#0060A9", "#CE1141"
SMU_NAVY, SMU_RED = "#28356A", "#CC0035"
LABEL_COLORS = {"growing": "#16A34A", "stable": "#2563EB", "decline": "#D97706", "discontinued": "#9CA3AF"}
LABEL_WORDS = {"growing": "Growing", "stable": "Stable", "decline": "Declining", "discontinued": "Discontinued"}

DEFAULT_FLOOR = 250   # tested at this; the slider lets Eurpac move it
FLOORS = [12, 52, 100, 250, 500, 1000, 2500, 5000]


@st.cache_data(show_spinner=False)
def load_predictions():
    return pd.read_parquet(DATA / "predictions.parquet")


@st.cache_data(show_spinner=False)
def load_labels():
    return pd.read_parquet(DATA / "labels.parquet")


@st.cache_data(show_spinner=False)
def load_weekly():
    return pd.read_parquet(DATA / "weekly.parquet")


def sidebar_controls():
    """The size floor, at the top of the sidebar on every page. Remembered as you move around."""
    st.session_state.setdefault("floor", DEFAULT_FLOOR)
    st.session_state.setdefault("watch", [])
    with st.sidebar:
        st.markdown("## Settings")
        st.session_state["floor"] = st.select_slider(
            "Size floor: cases sold last year", options=FLOORS, value=st.session_state["floor"],
            help="Brands below this are hidden on every page. The models were tested at 250. "
                 "Eurpac can set this to whatever 'too small to care about' means to them.")
    return st.session_state["floor"]


def current_floor():
    """The remembered floor, for pages that use it but do not need the slider."""
    st.session_state.setdefault("floor", DEFAULT_FLOOR)
    st.session_state.setdefault("watch", [])
    return st.session_state["floor"]


def sidebar_watchlist():
    """The watchlist, at the bottom of the sidebar on every page."""
    watch = st.session_state.setdefault("watch", [])
    with st.sidebar:
        st.markdown(f"## Watchlist ({len(watch)})")
        if watch:
            for b in watch:
                c1, c2 = st.columns([5, 1])
                c1.caption(b)
                if c2.button("x", key=f"rm_{b}", help="Remove"):
                    watch.remove(b)
                    st.rerun()
            st.download_button("Download watchlist", "\n".join(watch), "watchlist.txt", width="stretch")
        else:
            st.caption("Pin brands from the List or Brand page.")


def explain(title, text):
    """A collapsed 'What am I looking at?' box at the top of a page."""
    with st.expander(f"What am I looking at? {title}", expanded=False):
        st.markdown(text)


def header(title):
    left, mid, right = st.columns([2, 5, 2])
    with left:
        st.image(str(ASSETS / "eurpac_logo.png"), width=190)
    with mid:
        st.markdown(f'<div class="hdr"><div class="hdr-app">{APP_NAME}</div>'
                    f'<div class="hdr-page">{title}</div></div>', unsafe_allow_html=True)
    with right:
        smu = ASSETS / "smu_logo.png"
        if smu.exists():
            st.image(str(smu), width=150)
        else:
            st.markdown('<div class="smu-text">SMU<span>Data Science</span></div>', unsafe_allow_html=True)
    st.markdown('<hr class="hdr-rule">', unsafe_allow_html=True)


def label_chip(label):
    return (f'<span class="chip" style="background:{LABEL_COLORS[label]}22;color:{LABEL_COLORS[label]};'
            f'border:1px solid {LABEL_COLORS[label]}66">{LABEL_WORDS[label]}</span>')


CSS = f"""
<style>
  header[data-testid="stHeader"] {{ background: transparent; height: 0; }}
  [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu {{ display: none; }}
  .block-container {{ padding-top: 2.2rem; padding-bottom: 2rem; max-width: 1400px; }}
  .hdr {{ text-align:center; }}
  .hdr-app {{ font-size: 30px; font-weight: 800; color: {EURPAC_GRAY}; letter-spacing: .02em; }}
  .hdr-page {{ font-size: 15px; color: {EURPAC_BLUE}; text-transform: uppercase; letter-spacing: .12em; margin-top: 2px; }}
  .hdr-rule {{ border: none; border-top: 3px solid {EURPAC_RED}; margin: 6px 0 18px; }}
  .smu-text {{ text-align:right; font-size: 26px; font-weight: 800; color: {SMU_NAVY}; line-height: 1; }}
  .smu-text span {{ display:block; font-size: 11px; font-weight: 600; color: {SMU_RED}; letter-spacing: .14em; text-transform: uppercase; margin-top: 3px; }}
  .chip {{ display:inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
  .big {{ font-size: 34px; font-weight: 800; color: {EURPAC_GRAY}; line-height: 1.1; }}
  .big-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: #6B7280; }}
  .card {{ background: #F3F4F6; border-radius: 12px; padding: 14px 18px; }}
  .reason {{ font-size: 15px; color: #374151; }}
  section[data-testid="stSidebar"] {{ background: #F8FAFC; border-right: 1px solid #E5E7EB; }}
  section[data-testid="stSidebar"] h2 {{ color: {EURPAC_GRAY}; font-size: 16px; }}
  section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a span {{ font-size: 15px; }}
  div[data-baseweb="tag"] {{ background: {EURPAC_BLUE}22 !important; color: {EURPAC_GRAY} !important; }}
  div[data-baseweb="tag"] span {{ color: {EURPAC_GRAY} !important; }}
  .foot {{ color: #9CA3AF; font-size: 12px; text-align: center; margin-top: 30px; }}
</style>
"""


def footer():
    st.markdown(f'<div class="foot">{APP_NAME} · SMU MSDS Capstone, Fall 2026 · Nunnally and Streeter · '
                f'NIQ data under NDA, runs locally</div>', unsafe_allow_html=True)
