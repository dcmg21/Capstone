"""Shared pieces: data loading, colors, the header, the sidebar. Every page imports this."""

import base64
import copy
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

DEFAULT_FLOOR = 500   # Eurpac's choice (models were tested at 250); the slider lets them move it
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


@st.cache_data(show_spinner=False)
def load_suppliers():
    """brand -> supplier (NIQ's BRAND OWNER). Empty if the data was built before suppliers were added."""
    path = DATA / "suppliers.parquet"
    return pd.read_parquet(path) if path.exists() else pd.DataFrame(columns=["brand", "supplier"])


@st.cache_data(show_spinner=False)
def load_brand_table():
    """The predictions table plus each brand's supplier and its cases the year before.
    The Brand List's supplier filter and both supplier pages read this."""
    p = load_predictions().merge(load_suppliers(), on="brand", how="left")
    w = load_weekly()
    last = int(w["week"].max())
    prior = w[(w["week"] > last - 104) & (w["week"] <= last - 52)].groupby("brand")["cases"].sum()
    p["cases_prior_year"] = p["brand"].map(prior).fillna(0.0)
    return p


def filter_state(name, defaults):
    """A page's filter values, kept in session_state so they survive a trip to another page.
    Returns the values and a function that names each widget. Use it as
        f["x"] = st.slider(..., value=f["x"], key=key("x"))
    clear_filters() changes every widget's name, so they all start again from the defaults."""
    f = st.session_state.setdefault(name, copy.deepcopy(defaults))
    for k, v in defaults.items():                       # a filter added after this session started
        f.setdefault(k, copy.deepcopy(v))
    gen = st.session_state.setdefault(name + "_gen", 0)
    return f, (lambda k: f"{name}_{k}_{gen}")


def clear_filters(name, defaults):
    st.session_state[name] = copy.deepcopy(defaults)
    st.session_state[name + "_gen"] = st.session_state.get(name + "_gen", 0) + 1
    st.rerun()


def filters_header(slot, title, name, defaults, f, skip=("sort_by",)):
    """Fills the top of a filter block: the title, how many filters are on, and a Clear button."""
    n_on = sum(f[k] != defaults[k] for k in defaults if k not in skip)
    with slot:
        st.markdown(f"## {title}")
        c1, c2 = st.columns([3, 2], vertical_alignment="center")
        c1.caption("No filters on" if n_on == 0 else f"{n_on} filter{'s' if n_on > 1 else ''} on")
        if c2.button("Clear", key=name + "_clear", disabled=n_on == 0, width="stretch", help="Put every filter back to its starting value"):
            clear_filters(name, defaults)


def sidebar_controls(title=True):
    """The size floor, in the sidebar on Home, the Brand List and the Supplier List. Remembered as you move around.
    title=False leaves out the "Settings" heading, for pages that put the slider under their own Search box."""
    st.session_state.setdefault("floor", DEFAULT_FLOOR)
    st.session_state.setdefault("watch", [])
    with st.sidebar:
        if title:
            st.markdown("## Settings")
        # the key gives the slider one fixed identity; without it every second change was ignored
        st.session_state["floor"] = st.select_slider(
            "Size floor: cases sold last year", options=FLOORS, value=st.session_state["floor"], key="floor_slider",
            help="Brands below this are left out of the Home numbers, the Brand List and the Supplier List (a brand's own page still opens). The models were tested at 250. "
                 "Eurpac can set this to whatever 'too small to care about' means to them.")
    return st.session_state["floor"]


def current_floor():
    """The remembered floor, for pages that use it but do not need the slider."""
    st.session_state.setdefault("floor", DEFAULT_FLOOR)
    st.session_state.setdefault("watch", [])
    return st.session_state["floor"]


def sidebar_watchlist(pin_from=None):
    """The watchlist, at the bottom of the sidebar on every page.
    pin_from: brand names in ranked order. The Brand List passes its current ranking so the top N can be pinned here."""
    watch = st.session_state.setdefault("watch", [])
    with st.sidebar:
        st.markdown(f"## Watchlist ({len(watch)})")
        if pin_from is not None:
            c_n, c_b = st.columns([2, 3], vertical_alignment="center")
            n = c_n.number_input("How many to pin", 1, 100, st.session_state.get("pin_n", 10), label_visibility="collapsed", key="pin_n_box")
            st.session_state["pin_n"] = n
            if c_b.button(f"Pin top {n}", width="stretch", help="Adds the top brands of the current ranking to the watchlist"):
                watch.extend(b for b in pin_from[:int(n)] if b not in watch)
                st.rerun()
        if watch:
            box = st.container(height=230) if len(watch) > 6 else st.container()     # a long list scrolls
            for b in watch:
                c1, c2 = box.columns([5, 1], vertical_alignment="center")
                c1.caption(b)
                if c2.button("x", key=f"rm_{b}", help="Remove"):
                    watch.remove(b)
                    st.rerun()
            st.download_button("Download watchlist", "\n".join(watch), "watchlist.txt", width="stretch")
        else:
            st.caption("Pin brands from the Brand List or One Brand.")


def explain(title, text):
    """A collapsed 'What am I looking at?' box at the top of a page."""
    with st.expander(f"What am I looking at? {title}", expanded=False):
        st.markdown(text)


@st.cache_data(show_spinner=False)
def _logo(name):
    """A logo file as an inline image source, or None if the file is not there."""
    path = ASSETS / name
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode() if path.exists() else None


def header(title):
    """Eurpac logo, app name and page, SMU mark: one row, all three centered on the same line."""
    eurpac, smu = _logo("eurpac_logo.png"), _logo("smu_logo.png")
    left = f'<img src="{eurpac}" alt="Eurpac">' if eurpac else ""
    right = (f'<img src="{smu}" alt="SMU">' if smu else
             '<div class="smu-bar"></div><div class="smu-text">SMU<span>Data Science</span></div>')
    st.markdown(f'<div class="hdr-row"><div class="hdr-l">{left}</div>'
                f'<div class="hdr"><div class="hdr-app">{APP_NAME}</div><div class="hdr-page">{title}</div></div>'
                f'<div class="hdr-r">{right}</div></div><hr class="hdr-rule">', unsafe_allow_html=True)


TOL = 0.0005   # the stored numbers are rounded to 3 decimals; the rules ran on the exact ones, so allow for that at a boundary


def decline_fired(r):
    """For a Declining brand: (lost shelf this year?, lost most of its shelf ever?)."""
    tr = 1.0 if pd.isna(r["store_trend"]) else r["store_trend"]
    return tr < 0.90 + TOL, r["stores_vs_best"] < 0.40 + TOL


def times(ratio):
    """A this-year / last-year ratio as words: '+41%', '-22%', or '7.6x' for big jumps."""
    if ratio is None or pd.isna(ratio):
        return "n/a"
    if ratio >= 3:
        return f"{ratio:.1f}x" if ratio < 10 else f"{ratio:.0f}x"
    return f"{ratio - 1:+.0%}"


def shelf_change(tr):
    """Store trend as words, for the reason lines."""
    if pd.isna(tr):
        return "no prior year"
    return f"{times(tr)} vs a year ago"


def short_reason(r):
    """Which number decided the label, in a few words. r has sales_vs_best, stores_vs_best, store_trend, label."""
    sb, st_, tr = r["sales_vs_best"], r["stores_vs_best"], r["store_trend"]
    if pd.isna(sb) or pd.isna(st_):
        return "no sales or shelf on record"            # a brand in NIQ's list that never sold: there is no best to compare with
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
    """The colored label pill. gloss=True adds what it measures, e.g. 'Declining: lost shelf space'."""
    text = LABEL_WORDS[label] + (f": {LABEL_GLOSS[label]}" if gloss else "")
    return (f'<span class="chip" style="background:{LABEL_COLORS[label]}22;color:{LABEL_COLORS[label]};'
            f'border:1px solid {LABEL_COLORS[label]}66">{text}</span>')


CSS = f"""
<style>
  header[data-testid="stHeader"] {{ background: transparent; height: 0; }}
  [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu {{ display: none; }}
  .block-container {{ padding-top: 2.2rem; padding-bottom: 2rem; max-width: 1400px; }}
  .hdr-row {{ display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 20px; padding: 4px 0 8px; }}
  .hdr-l {{ justify-self: start; display: flex; align-items: center; min-width: 0; }}
  .hdr-l img {{ height: 34px; width: auto; max-width: 100%; display: block; }}
  .hdr-r {{ justify-self: end; display: flex; align-items: center; gap: 10px; }}
  .hdr-r img {{ height: 44px; width: auto; display: block; }}
  .hdr {{ text-align: center; white-space: nowrap; }}
  .hdr-app {{ font-size: 32px; font-weight: 800; color: {EURPAC_GRAY}; letter-spacing: .02em; line-height: 1.05; }}
  .hdr-page {{ font-size: 14px; color: {EURPAC_BLUE}; text-transform: uppercase; letter-spacing: .12em; margin-top: 4px; }}
  .hdr-rule {{ border: none; border-top: 3px solid {EURPAC_RED}; margin: 6px 0 18px; }}
  .smu-bar {{ width: 3px; height: 38px; background: {SMU_RED}; border-radius: 2px; flex: none; }}
  .smu-text {{ font-size: 30px; font-weight: 800; color: {SMU_NAVY}; line-height: 1; }}
  .smu-text span {{ display: block; font-size: 10px; font-weight: 700; color: {SMU_RED}; letter-spacing: .1em; text-transform: uppercase;
                    margin-top: 4px; white-space: nowrap; }}
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
  section[data-testid="stSidebar"] h2 {{ color: #6B7280; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .1em;
                                         border-top: 1px solid #E5E7EB; padding-top: 14px; margin-top: 4px; }}
  section[data-testid="stSidebar"] [data-testid="stExpander"] details {{ background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; }}
  section[data-testid="stSidebar"] [data-testid="stExpander"] summary {{ font-weight: 600; color: {EURPAC_GRAY}; }}
  .card.small .big {{ font-size: 26px; }}
  .sup-name {{ font-size: 26px; font-weight: 800; color: {EURPAC_GRAY}; line-height: 1.15; }}
  section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a span {{ font-size: 15px; }}
  div[data-baseweb="tag"] {{ background: {EURPAC_BLUE}22 !important; color: {EURPAC_GRAY} !important; }}
  div[data-baseweb="tag"] span {{ color: {EURPAC_GRAY} !important; }}
  .foot {{ color: #9CA3AF; font-size: 12px; text-align: center; margin-top: 30px; }}
</style>
"""


def footer():
    st.markdown(f'<div class="foot">{APP_NAME} · SMU MSDS Capstone, Fall 2026 · Nunnally and Streeter · '
                f'NIQ data under NDA, runs locally</div>', unsafe_allow_html=True)
