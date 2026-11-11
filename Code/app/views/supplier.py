"""One supplier: its numbers, its weekly sales, and every brand it owns."""

import io
import re

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (EURPAC_BLUE, GLOSS_LINE, LABEL_COLORS, LABEL_WORDS, current_floor, explain, footer, header, load_brand_table,
                    load_labels, load_weekly, sidebar_watchlist, times, why_label)

header("One Supplier")
floor = current_floor()
b = load_brand_table()
year = int(b["as_of"].iloc[0])
if b["supplier"].isna().all():
    st.error("The data files have no suppliers yet. From the Code folder run:  python app\\build_app_data.py  then restart the app.")
    st.stop()

explain("One supplier", f"""
Everything one supplier (NIQ's "brand owner") sells in this market. **Every number and chart on the page covers the
brands listed in the table at the bottom**: its brands that sold at least {floor} cases in {year}, or all of its brands
if you switch on "Include its smaller brands."

- **Sales vs a year ago**: those brands' cases in {year} against the same brands' cases in {year - 1}.
- **Viable today**: how many of them are labeled stable or growing. The labels are about shelf space more than sales: {GLOSS_LINE}.

Click a brand in the table to open its own page.
""")

# ---- pick a supplier -------------------------------------------------------------
st.page_link("views/suppliers.py", label="Supplier List", icon=":material/arrow_back:")
names = b.groupby("supplier")["cases_last_year"].sum().sort_values(ascending=False).index.tolist()
default = st.session_state.get("supplier", names[0])
c_pick, c_all = st.columns([3, 2], vertical_alignment="bottom")
name = c_pick.selectbox("Supplier", names, index=names.index(default) if default in names else 0, key="supplier_pick",
                        help="Type to search. Sorted by cases sold.")   # the key keeps one identity, so every pick registers
st.session_state["supplier"] = name
mine = b[b["supplier"] == name]
n_above = int((mine["cases_last_year"] >= floor).sum())
include_all = c_all.toggle(f"Include its smaller brands (under {floor} cases)", value=(n_above == 0),
                           help=f"{name.title()} owns {len(mine):,} brands in the data; {n_above:,} sold at least {floor} cases in {year}.")
shown = (mine if include_all else mine[mine["cases_last_year"] >= floor]).sort_values("cases_last_year", ascending=False)
if shown.empty:
    st.info(f"None of this supplier's {len(mine):,} brands sold {floor} cases in {year}. Switch on \"Include its smaller brands\" to see them.")
    sidebar_watchlist()
    footer()
    st.stop()

# ---- header: name and the numbers ------------------------------------------------------------
cases, prior = shown["cases_last_year"].sum(), shown["cases_prior_year"].sum()
n_viable, n_growing = int(shown["viable"].sum()), int((shown["label"] == "growing").sum())
st.markdown(f'<div class="sup-name">{name.title()}</div>', unsafe_allow_html=True)
st.caption(f"{len(shown):,} of its {len(mine):,} brands shown" + ("" if include_all else f" (those above the {floor}-case floor)"))
cards = st.columns(4)
for col, num, text, tip in [
    (cards[0], f"{len(shown):,}", "brands", "The brands in the table below"),
    (cards[1], f"{cases:,.0f}", f"cases in {year}", "9-liter cases those brands sold in the last 52 weeks"),
    (cards[2], times(cases / prior) if prior > 0 else "n/a", "sales vs a year ago", f"Those brands' cases in {year} against the same brands' cases in {year - 1}"),
    (cards[3], f"{n_viable:,} of {len(shown):,}", "viable today", f"Labeled stable or growing. {n_growing:,} of them are growing"),
]:
    col.markdown(f'<div class="card small" title="{tip}"><div class="big">{num}</div><div class="big-label">{text}</div></div>',
                 unsafe_allow_html=True)
st.markdown("")

# ---- pictures: weekly sales, labels, categories ---------------------------------------------------
left, right = st.columns([3, 2])
with left:
    weekly = load_weekly()
    wk = weekly[weekly["brand"].isin(shown["brand"])].groupby("period_date")["cases"].sum().sort_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=wk.index, y=wk.values, name="each week", hoverinfo="skip",
                             line=dict(color="#93C5FD", width=1), opacity=0.7))
    fig.add_trace(go.Scatter(x=wk.index, y=wk.rolling(13).mean(), name="13-week average",
                             hovertemplate="%{x|%b %d, %Y}<br>%{y:,.0f} cases a week (13-week average)<extra></extra>",
                             line=dict(color=EURPAC_BLUE, width=2.5)))
    fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.12),
                      plot_bgcolor="white", paper_bgcolor="white", hoverlabel=dict(bgcolor="white", font_size=13))
    fig.update_yaxes(rangemode="tozero", gridcolor="#F3F4F6")
    st.markdown("**Sales: cases per week, these brands together**")
    st.plotly_chart(fig, width="stretch")
with right:
    order = ["growing", "stable", "decline", "discontinued"]
    counts = shown["label"].value_counts().reindex(order).fillna(0).astype(int)
    fig_l = go.Figure(go.Bar(y=[LABEL_WORDS[k] for k in order][::-1], x=counts.values[::-1], orientation="h",
                             marker_color=[LABEL_COLORS[k] for k in order][::-1], text=counts.values[::-1], textposition="outside",
                             hovertemplate="%{x} brands %{y}<extra></extra>", cliponaxis=False))
    fig_l.update_layout(height=160, margin=dict(l=10, r=30, t=6, b=6), plot_bgcolor="white", paper_bgcolor="white")
    fig_l.update_xaxes(visible=False)
    st.markdown("**Its brands by label today**")
    st.plotly_chart(fig_l, width="stretch")

    by_cat = shown.groupby(shown["category"].astype(str))["cases_last_year"].sum().sort_values(ascending=False).head(6)
    fig_c = go.Figure(go.Bar(y=[c.title() for c in by_cat.index][::-1], x=by_cat.values[::-1], orientation="h", marker_color="#9CA3AF",
                             text=[f"{v / cases:.0%}" if cases else "" for v in by_cat.values[::-1]], textposition="outside",
                             hovertemplate="%{y}<br>%{x:,.0f} cases<extra></extra>", cliponaxis=False))
    fig_c.update_layout(height=40 + 26 * len(by_cat), margin=dict(l=10, r=40, t=6, b=6), plot_bgcolor="white", paper_bgcolor="white")
    fig_c.update_xaxes(visible=False)
    st.markdown(f"**Where its cases come from** (share of its {year} cases by category)")
    st.plotly_chart(fig_c, width="stretch")

# ---- every brand it owns -------------------------------------------------------------------
a, c1, c2 = st.columns([3, 1, 1], vertical_alignment="bottom")
a.markdown(f"#### Its brands ({len(shown):,})")
a.caption("Biggest first. Click a row to open that brand.")
show = shown[["brand", "category", "price_tier", "cases_last_year", "years_of_data", "label",
              "chance_viable_next_year", "chance_growing_next_year", "vs_category"]].copy()
nums = load_labels().query("as_of == @year").set_index("brand")[["sales_vs_best", "stores_vs_best", "store_trend", "label"]]
show["why"] = [why_label(r) for r in nums.reindex(show["brand"]).to_dict("records")]
show["label"] = show["label"].map(LABEL_WORDS)
show.columns = ["Brand", "Category", "Price tier", f"Cases {year}", "Years of data", "Label today",
                f"Viable {year + 1}", f"Growing {year + 1}", "Sales vs category", "Why this label"]
picked_row = st.dataframe(
    show, hide_index=True, height=min(460, 60 + 35 * len(show)), on_select="rerun", selection_mode="single-row",
    column_config={
        "Brand": st.column_config.TextColumn(width=240),
        "Category": st.column_config.TextColumn(width=160),
        "Price tier": st.column_config.TextColumn(width=105),
        f"Cases {year}": st.column_config.NumberColumn(format="localized", width=100, help=f"9-liter cases sold in {year}"),
        "Years of data": st.column_config.NumberColumn(format="%.1f", width=110),
        "Label today": st.column_config.TextColumn(width=110, help=f"At the end of {year}. {GLOSS_LINE}"),
        f"Viable {year + 1}": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1, width=120,
                                                             help=f"Model's chance the brand is stable or growing at the end of {year + 1}. "
                                                                  "Blank for brands that sold under 12 cases"),
        f"Growing {year + 1}": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1, width=125,
                                                              help=f"Model's chance the brand is growing at the end of {year + 1}"),
        "Sales vs category": st.column_config.NumberColumn(format="%.2f", width=120,
                                                           help="The brand's sales change divided by its category's. 1.00 = moved with the category"),
        "Why this label": st.column_config.TextColumn(width=400, help="What the label means, then the number that decided it"),
    },
)
rows = picked_row.selection.rows if picked_row and picked_row.selection else []
if rows:
    st.session_state["brand"] = shown.iloc[rows[0]]["brand"]
    st.switch_page("views/brand.py")

if n_above and c1.button("Open on the Brand List", width="stretch",
                         help="Opens the Brand List showing only this supplier's brands, where you can filter and rank them. "
                              "Your other Brand List filters stay as you left them"):
    lf = st.session_state.setdefault("list_filters", {})
    lf["suppliers"] = [name]
    st.switch_page("views/list.py")
safe_name = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:40]
try:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        show.to_excel(xl, sheet_name="brands", index=False)
    c2.download_button("Download as Excel", buf.getvalue(), f"brand_radar_{safe_name}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
except ImportError:
    c2.download_button("Download as CSV", show.to_csv(index=False).encode(), "brand_radar_supplier.csv", "text/csv", width="stretch")

sidebar_watchlist()
footer()
