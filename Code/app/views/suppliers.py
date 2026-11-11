"""Suppliers: every supplier side by side, each one summed up from its brands above the size floor."""

import io

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (LABEL_COLORS, LABEL_WORDS, explain, filter_state, filters_header, footer, header, load_brand_table,
                    sidebar_controls, sidebar_watchlist)

header("Supplier List")
top = st.sidebar.container()             # sidebar order: title and Clear, Search, size floor, then the rest
search_box = st.sidebar.container()
floor = sidebar_controls(title=False)
b = load_brand_table()
year = int(b["as_of"].iloc[0])
if b["supplier"].isna().all():
    st.error("The data files have no suppliers yet. From the Code folder run:  python app\\build_app_data.py  then restart the app.")
    st.stop()

explain("The supplier list", f"""
One row per **supplier** (NIQ's "brand owner"). Every number on a row is added up from that supplier's brands
that sold at least **{floor} cases** in {year} (the size floor in the sidebar), the same brands the Brand List shows.

- **Brands**: how many of its brands are above the floor.
- **Cases {year}** and **Sales vs a year ago**: those brands' cases this year, and the change from the same brands' cases last year.
- **Growing today** and **Viable today**: how many of those brands are labeled growing, and the share labeled stable or growing.
- **Best bet**: its brand with the highest chance of growing.

A supplier spans categories and price tiers, so those are on the supplier's own page, not here. NIQ lists some
companies under more than one owner name (a parent and a subsidiary, say); they are shown as NIQ has them.

Click a row to open that supplier and see every brand it owns.
""")

# ---- one row per supplier, from its brands above the floor -----------------------------------
above = b[(b["cases_last_year"] >= floor) & b["chance_growing_next_year"].notna() & b["supplier"].notna()].copy()
above["is_growing"] = above["label"] == "growing"
g = above.groupby("supplier")
t = g.agg(brands=("brand", "size"), cases=("cases_last_year", "sum"), cases_prior=("cases_prior_year", "sum"),
          growing=("is_growing", "sum"), viable=("viable", "sum")).reset_index()
t["sales_change"] = (t["cases"] / t["cases_prior"].where(t["cases_prior"] > 0) - 1) * 100       # percent; blank if nothing last year
t["share_viable"] = t["viable"] / t["brands"] * 100
best = above.loc[g["chance_growing_next_year"].idxmax(), ["supplier", "brand"]].rename(columns={"brand": "best_bet"})
t = t.merge(best, on="supplier")

# ---- filters -----------------------------------------------------------------
RANKS = {"cases sold": "cases", "number of brands": "brands",
         "brands growing today": "growing", "share viable today": "share_viable", "sales vs a year ago": "sales_change"}
DEFAULTS = dict(search="", sort_by="cases sold", min_brands=1)
f, key = filter_state("supplier_filters", DEFAULTS)
if f["sort_by"] not in RANKS:                 # a ranking that has since been removed
    f["sort_by"] = DEFAULTS["sort_by"]
with st.sidebar:
    f["search"] = search_box.text_input("Search", value=f["search"], placeholder="supplier name", key=key("search"))
    f["sort_by"] = st.selectbox("Rank by", list(RANKS), index=list(RANKS).index(f["sort_by"]), key=key("sort_by"))
    f["min_brands"] = st.select_slider("Only suppliers with this many brands or more", options=[1, 2, 3, 5, 10, 20], value=f["min_brands"],
                                       key=key("min_brands"),
                                       help="Hides small suppliers. Set it to 5 and you only see suppliers that own at least 5 brands above the size floor. "
                                            "Useful because a supplier with one brand is always 0% or 100% viable.")
    filters_header(top, "Find suppliers", "supplier_filters", DEFAULTS, f)

view = t[t["brands"] >= f["min_brands"]]
if f["search"]:
    view = view[view["supplier"].str.upper().str.contains(f["search"].upper(), regex=False)]
view = view.sort_values(RANKS[f["sort_by"]], ascending=False, na_position="last").reset_index(drop=True)

# ---- the numbers at a glance -------------------------------------------------------------
top10 = t.nlargest(10, "cases")["cases"].sum() / t["cases"].sum() if t["cases"].sum() else 0
c1, c2, c3, c4 = st.columns(4)
for col, num, text, tip in [
    (c1, f"{len(t):,}", f"suppliers with a brand above {floor} cases", "Every supplier that owns at least one brand on the Brand List at this floor"),
    (c2, f"{int(t['brands'].sum()):,}", "brands they own above the floor", "The same brands the Brand List shows at this floor"),
    (c3, f"{top10:.0%}", "of those cases sold by the 10 biggest", "The ten suppliers with the most cases, as a share of all cases above the floor"),
    (c4, f"{int((t['growing'] > 0).sum()):,}", "suppliers with a growing brand today", "Suppliers that own at least one brand labeled growing"),
]:
    col.markdown(f'<div class="card" title="{tip}"><div class="big">{num}</div><div class="big-label">{text}</div></div>',
                 unsafe_allow_html=True)
st.markdown("")

# ---- picture: the top of the ranking, by label ------------------------------------------------
n_bars = min(15, len(view))
if n_bars:
    lead = view.head(n_bars).sort_values("brands", ascending=False)["supplier"].tolist()   # longest bar first
    mix = (above[above["supplier"].isin(lead)].groupby(["supplier", "label"]).size().unstack(fill_value=0)
           .reindex(index=lead[::-1]))                                   # reversed so the longest bar is on top
    fig = go.Figure()
    for lab in ["growing", "stable", "decline", "discontinued"]:
        if lab in mix.columns:
            fig.add_trace(go.Bar(y=[s.title() for s in mix.index], x=mix[lab], name=LABEL_WORDS[lab], orientation="h",
                                 marker_color=LABEL_COLORS[lab],
                                 hovertemplate="%{y}<br>%{x} brands " + LABEL_WORDS[lab].lower() + "<extra></extra>"))
    fig.update_layout(barmode="stack", height=100 + 26 * n_bars, margin=dict(l=10, r=10, t=50, b=10),
                      plot_bgcolor="white", paper_bgcolor="white",
                      legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, traceorder="normal"),
                      hoverlabel=dict(bgcolor="white", font_size=13))
    fig.update_xaxes(gridcolor="#F3F4F6", title_text="brands above the floor")
    st.markdown(f"**The top {n_bars} by {f['sort_by']}: how many brands each has, and what they are labeled today**")
    st.caption("Sorted from the most brands to the fewest. Each bar is one supplier; the colors are its brands by label.")
    st.plotly_chart(fig, width="stretch")

# ---- the table ---------------------------------------------------------------
a, c = st.columns([4, 1])
a.markdown(f"**{len(view):,} suppliers**, ranked by **{f['sort_by']}**. Click a row to open that supplier.")
show = view[["supplier", "brands", "cases", "sales_change", "growing", "share_viable", "best_bet"]].copy()
show.insert(0, "#", range(1, len(show) + 1))
show.columns = ["#", "Supplier", "Brands", f"Cases {year}", "Sales vs a year ago", "Growing today", "Viable today",
                "Best bet"]
picked_row = st.dataframe(
    show, hide_index=True, height=520, on_select="rerun", selection_mode="single-row",
    column_config={
        "#": st.column_config.NumberColumn(width=55, help="Position in this ranking"),
        "Supplier": st.column_config.TextColumn(width=280, help="NIQ's brand owner"),
        "Brands": st.column_config.NumberColumn(width=80, help=f"Its brands that sold at least {floor} cases in {year}"),
        f"Cases {year}": st.column_config.NumberColumn(format="localized", width=115, help=f"9-liter cases those brands sold in {year}"),
        "Sales vs a year ago": st.column_config.NumberColumn(format="%+.0f%%", width=130,
                                                             help=f"Those brands' cases in {year} against the same brands' cases in {year - 1}. "
                                                                  "Blank if they sold nothing the year before"),
        "Growing today": st.column_config.NumberColumn(width=115, help="How many of those brands are labeled growing"),
        "Viable today": st.column_config.ProgressColumn(format="%.0f%%", min_value=0, max_value=100, width=130,
                                                        help="Share of those brands labeled stable or growing"),
        "Best bet": st.column_config.TextColumn(width=260, help="Its brand with the highest chance of growing"),
    },
)
rows = picked_row.selection.rows if picked_row and picked_row.selection else []
if rows:
    st.session_state["supplier"] = view.iloc[rows[0]]["supplier"]
    st.switch_page("views/supplier.py")

try:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        show.to_excel(xl, sheet_name="suppliers", index=False)
    c.download_button("Download as Excel", buf.getvalue(), f"brand_radar_suppliers_floor{floor}.xlsx",
                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
except ImportError:
    c.download_button("Download as CSV", show.to_csv(index=False).encode(), f"brand_radar_suppliers_floor{floor}.csv",
                      "text/csv", width="stretch", help="pip install openpyxl for Excel")

sidebar_watchlist()
footer()
