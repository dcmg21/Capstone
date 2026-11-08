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
# what each label actually measures, in a few words: the labels are about shelf space more than sales
LABEL_GLOSS = {"growing": "near its best and adding shelf", "stable": "holding its shelf",
               "decline": "lost shelf space", "discontinued": "gone from shelves"}
GLOSS_LINE = "; ".join(f"{LABEL_WORDS[k]} = {v}" for k, v in LABEL_GLOSS.items())

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
    """The size floor, at the top of the sidebar on Home and The List. Remembered as you move around."""
    st.session_state.setdefault("floor", DEFAULT_FLOOR)
    st.session_state.setdefault("watch", [])
    with st.sidebar:
        st.markdown("## Settings")
        st.session_state["floor"] = st.select_slider(
            "Size floor: cases sold last year", options=FLOORS, value=st.session_state["floor"],
            help="Brands below this are hidden from the Home numbers and The List (a brand's own page still opens). The models were tested at 250. "
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


TOL = 0.0005   # the stored numbers are rounded to 3 decimals; the rules ran on the exact ones, so allow for that at a boundary


def decline_fired(r):
    """For a Declining brand: (lost shelf this year?, lost most of its shelf ever?)."""
    tr = 1.0 if pd.isna(r["store_trend"]) else r["store_trend"]
    return tr < 0.90 + TOL, r["stores_vs_best"] < 0.40 + TOL


def shelf_change(tr):
    """Store trend as words, with the huge-from-nothing case handled."""
    if pd.isna(tr):
        return "no prior year"
    return "up many times over" if tr >= 5 else f"{tr - 1:+.0%} vs a year ago"


def short_reason(r):
    """Which number decided the label, in a few words. r has sales_vs_best, stores_vs_best, store_trend, label."""
    sb, st_, tr = r["sales_vs_best"], r["stores_vs_best"], r["store_trend"]
    if r["label"] == "discontinued":
        return f"sales {sb:.0%} of its best, shelf {st_:.0%} of its best"
    if r["label"] == "growing":
        return f"sales {sb:.0%} of its best, shelf {shelf_change(tr)}"
    if r["label"] == "decline":
        this_year, ever = decline_fired(r)
        parts = ([f"shelf {shelf_change(tr)}"] if this_year else []) + ([f"shelf {st_:.0%} of its best"] if ever else [])
        return ", ".join(parts) or f"shelf {shelf_change(tr)}"
    return f"shelf {st_:.0%} of its best, {shelf_change(tr)}"


def why_label(r):
    """Gloss first, then the number that decided it: 'lost shelf space: shelf 20% of its best'."""
    return f"{LABEL_GLOSS[r['label']]}: {short_reason(r)}"


def label_chip(label, gloss=False):
    """The colored label pill. gloss=True adds what it measures, e.g. 'Declining: losing shelf space'."""
    text = LABEL_WORDS[label] + (f": {LABEL_GLOSS[label]}" if gloss else "")
    return (f'<span class="chip" style="background:{LABEL_COLORS[label]}22;color:{LABEL_COLORS[label]};'
            f'border:1px solid {LABEL_COLORS[label]}66">{text}</span>')


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
  table.score {{ border-collapse: collapse; margin: 10px 0 6px; font-size: 15px; width: 100%; max-width: 820px; }}
  table.score th {{ text-align: center; font-weight: 600; color: #6B7280; font-size: 12px; text-transform: uppercase; letter-spacing: .06em; padding: 4px 14px 6px 0; border-bottom: 2px solid #E5E7EB; }}
  table.score td {{ text-align: center; padding: 9px 14px 9px 0; border-bottom: 1px solid #F3F4F6; color: #1F2937; }}
  table.score td.rowname {{ text-align: left; font-weight: 700; color: {EURPAC_GRAY}; }}
  table.score th:first-child {{ text-align: left; }}
  table.score .fired {{ font-weight: 700; padding: 2px 8px; border-radius: 6px; border: 2px solid {EURPAC_RED}; }}
  table.score td.rowname span {{ display: block; font-weight: 400; font-size: 12px; color: #9CA3AF; }}
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
