"""One brand: a sales-and-shelf scorecard, the chart, the label at every year-end, and the math behind it."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from common import (EURPAC_BLUE, GLOSS_LINE, LABEL_COLORS, LABEL_GLOSS, LABEL_WORDS, current_floor, explain, footer,
                    decline_fired, header, label_chip, load_labels, load_predictions, load_suppliers, load_weekly, short_reason,
                    sidebar_watchlist, times)

header("One Brand")
floor = current_floor()


# ---- words for the numbers ---------------------------------------------------------------
def pct(x, signed=False):
    if x is None or pd.isna(x):
        return "n/a"
    return f"{x:+.0%}" if signed else f"{x:.0%}"


change = times   # '+41%', '-22%', or '7.6x' for a big jump


def verdict(ratio):
    """Brand's change divided by the category's: ahead, keeping pace, or behind."""
    if ratio is None or pd.isna(ratio):
        return ""
    return "ahead" if ratio >= 1.1 else ("keeping pace" if ratio >= 0.9 else "behind")


def scorecard(r, cat):
    """Sales and shelf, each against the brand's own best, a year ago, and its category. One HTML table.
    The cell(s) that decided the label are marked."""
    g, cs = r.get("category_growth"), r.get("category_shelf_trend")
    sb, st_ = r["sales_vs_best"], r["stores_vs_best"]
    fired = {"sales_best": False, "shelf_best": False, "shelf_year": False}
    if r["label"] == "discontinued":
        fired.update(sales_best=True, shelf_best=True)
    elif r["label"] == "growing":
        fired.update(sales_best=True, shelf_year=True)
    elif r["label"] == "decline":
        fired.update(zip(["shelf_year", "shelf_best"], decline_fired(r)))
    mark = lambda text, on: f'<span class="fired">{text}</span>' if on else text
    sales_cat = f"{change(g)}" + (f" &nbsp;·&nbsp; brand <b>{verdict(r.get('vs_category'))}</b>" if pd.notna(g) else "")
    shelf_cat = f"{change(cs)}" + (f" &nbsp;·&nbsp; brand <b>{verdict(r.get('vs_shelf'))}</b>" if pd.notna(cs) else "")
    return f"""
<table class="score">
<tr><th></th><th>vs its own best</th><th>vs a year ago</th><th>category ({cat}) vs a year ago</th></tr>
<tr><td class="rowname">Sales <span>cases sold</span></td>
    <td>{mark(pct(sb), fired["sales_best"])}</td><td>{change(r['sales_growth'])}</td><td>{sales_cat}</td></tr>
<tr><td class="rowname">Shelf <span>% of stores carrying it</span></td>
    <td>{mark(pct(st_), fired["shelf_best"])}</td><td>{mark(change(r['store_trend']), fired["shelf_year"])}</td><td>{shelf_cat}</td></tr>
</table>"""


def hover_text(r, color, cat):
    """The year-end hover: the same scorecard, four short lines."""
    head = f'<span style="color:{color}; font-size:14px"><b>End of {r["as_of"]}: {LABEL_WORDS[r["label"]]}</b></span> ({LABEL_GLOSS[r["label"]]})'
    shelf = f"<b>Shelf:</b> {change(r['store_trend'])} vs a year ago · {pct(r['stores_vs_best'])} of its best"
    sales = f"<b>Sales:</b> {change(r['sales_growth'])} vs a year ago · {pct(r['sales_vs_best'])} of its best"
    parts = [head, shelf, sales]
    if pd.notna(r.get("category_growth")):
        parts.append(f"<b>{cat.title()}:</b> sales {change(r['category_growth'])} · shelf {change(r.get('category_shelf_trend'))}")
    return "<br>".join(parts) + "<extra></extra>"


def year_line(r, cat):
    """One caption per year-end under the chart."""
    s = f"**{r['as_of']} {LABEL_WORDS[r['label']]}** ({short_reason(r)}). Shelf {change(r['store_trend'])}, sales {change(r['sales_growth'])}"
    if pd.notna(r.get("category_growth")):
        s += f"; {cat} shelf {change(r.get('category_shelf_trend'))}, sales {change(r['category_growth'])}"
    return s + "."


p, labels, weekly = load_predictions(), load_labels(), load_weekly()
year = int(p["as_of"].iloc[0])
YEAR_END_WEEK = {2022: 104, 2023: 156, 2024: 208, 2025: 260, 2026: 312, 2027: 364}

explain("One brand", f"""
Everything about a brand is one of two things, **sales** (cases sold) or **shelf** (the share of the market's
stores that carry it, %ACV), measured three ways: against the brand's own best ever, against a year ago, and
against its category. That is the scorecard under the brand's name.

The label comes from the shelf row, with sales only deciding the two extremes: {GLOSS_LINE}.
So a brand can be "Declining" (lost shelf space) while its sales are up. Both are true, and the model's chances
use all of it.

The chart is the picture a person used to label brands by hand. Thin line = each week; thick line = 13-week
average, the view the labels are read from. Hover a year-end dot for that year's scorecard. "Step through"
under the chart shows every calculation, and the **How Labels Work** page explains all of it with worked examples.
""")

# ---- pick a brand -------------------------------------------------------------
names = p.sort_values("cases_last_year", ascending=False)["brand"].tolist()
default = st.session_state.get("brand", names[0])
c_pick, c_pin = st.columns([5, 1])
brand = c_pick.selectbox("Brand", names, index=names.index(default) if default in names else 0, key="brand_pick",
                         help="Type to search. Sorted by size.")       # the key keeps one identity, so every pick registers
st.session_state["brand"] = brand
watch = st.session_state["watch"]
c_pin.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
if brand in watch:
    if c_pin.button("Unpin", width="stretch"):
        watch.remove(brand)
        st.rerun()
else:
    if c_pin.button("Pin to watchlist", width="stretch"):
        watch.append(brand)
        st.rerun()

row = p[p["brand"] == brand].iloc[0]
hist = labels[labels["brand"] == brand].sort_values("as_of")
wk = weekly[weekly["brand"] == brand].sort_values("week")
cat = str(row["category"])
cat_l = cat.lower()
last = hist.iloc[-1] if len(hist) else None

# ---- header: name, the three big numbers, then the scorecard --------------------------------
c1, c2, c3, c4 = st.columns([3, 1.2, 1.2, 1.2])
with c1:
    st.markdown(f"### {brand}")
    st.markdown(f"{row['family']} · {cat} · {row['price_tier']}")
    supplier = load_suppliers().set_index("brand")["supplier"].get(brand)       # NIQ's brand owner, if the data has it
    if isinstance(supplier, str) and st.button(f"Supplier: {supplier.title()}", icon=":material/domain:", type="tertiary",
                                               help="Open this supplier: its numbers and every brand it owns"):
        st.session_state["supplier"] = supplier
        st.switch_page("views/supplier.py")
scored = bool(row[["chance_growing_next_year"]].notna().iloc[0])
for col, val, text, tip in [
    (c2, f"{row['cases_last_year']:,.0f}", f"cases in {year}", "9-liter cases sold in the last 52 weeks"),
    (c3, f"{row['chance_viable_next_year']:.0%}" if scored else "n/a", f"chance viable in {year + 1}",
     "Of 100 brands that looked like this one a year earlier, how many were stable or growing a year later"),
    (c4, f"{row['chance_growing_next_year']:.0%}" if scored else "n/a", f"chance growing in {year + 1}",
     "Of 100 brands that looked like this one a year earlier, how many were growing a year later"),
]:
    col.markdown(f'<div class="card" title="{tip}"><div class="big">{val}</div><div class="big-label">{text}</div></div>',
                 unsafe_allow_html=True)

if last is not None:
    st.markdown(scorecard(last, cat_l), unsafe_allow_html=True)
    st.markdown(f"Label today: {label_chip(row['label'], gloss=True)} &nbsp; <span class='reason'>{short_reason(last)}</span>"
                f" &nbsp; <span class='reason' style='color:#9CA3AF'>(outlined cells decided it)</span>", unsafe_allow_html=True)
else:
    st.markdown(f"Label today: {label_chip(row['label'], gloss=True)}", unsafe_allow_html=True)
if bool(row.get("comes_and_goes", False)):
    st.warning("**Comes and goes.** After it first started selling, this brand went half a year or more selling under a case a week "
               "(seasonal item, limited run or relaunch). Its \"vs its best\" and \"vs a year ago\" numbers measure a calendar as much "
               "as a trend, and both lines sit at zero where nothing sold. Read the label and the chances with that in mind.")
if not scored:
    st.info("Sold under 12 cases last year, so the model gives no chance. The label and chart still apply.")
elif row["cases_last_year"] < floor:
    st.info(f"This brand is below your {floor}-case floor, so it is hidden on the Brand List. Shown here because you asked for it.")

# ---- the chart (Kristin's view) -------------------------------------------------
overlay = st.toggle(f"Show the {cat_l} average, scaled to this brand", value=False,
                    help="The category's average brand, scaled to this brand's size: is the brand moving, or the whole category? "
                         "The scorecard above has the same comparison as numbers.")
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.07,
                    subplot_titles=("Sales: cases per week", "Shelf: % of stores carrying it"))
fig.add_trace(go.Scatter(x=wk["period_date"], y=wk["cases"], name="sales, each week", hoverinfo="skip",
                         line=dict(color="#93C5FD", width=1), opacity=0.7), row=1, col=1)
fig.add_trace(go.Scatter(x=wk["period_date"], y=wk["cases"].rolling(13).mean(), name="sales, 13-week average",
                         hovertemplate="%{x|%b %d, %Y}<br>%{y:,.1f} cases a week (13-week average)<extra></extra>",
                         line=dict(color=EURPAC_BLUE, width=2.5)), row=1, col=1)
fig.add_trace(go.Scatter(x=wk["period_date"], y=wk["store_coverage"], name="shelf, each week", hoverinfo="skip",
                         line=dict(color="#86EFAC", width=1), opacity=0.7), row=2, col=1)
fig.add_trace(go.Scatter(x=wk["period_date"], y=wk["store_coverage"].rolling(13).mean(), name="shelf, 13-week average",
                         hovertemplate="%{x|%b %d, %Y}<br>%ACV %{y:.0f} (13-week average)<extra></extra>",
                         line=dict(color="#15803D", width=2.5)), row=2, col=1)
if overlay:
    cat_brands = p.loc[p["category"].astype(str) == cat, "brand"]
    cat_wk = (weekly[weekly["brand"].isin(cat_brands)].groupby("period_date")[["cases", "store_coverage"]].mean())
    for col_, r_ in (("cases", 1), ("store_coverage", 2)):
        own = wk.set_index("period_date")[col_].rolling(13).mean()
        ref = cat_wk[col_].rolling(13).mean()
        scale = (own.mean() / ref.mean()) if ref.mean() else 1
        fig.add_trace(go.Scatter(x=ref.index, y=ref * scale, name=f"{cat_l} average, scaled", hoverinfo="skip",
                                 line=dict(color="#9CA3AF", width=2, dash="dash"), showlegend=(r_ == 1)), row=r_, col=1)
ymax = max(float(wk["cases"].max() or 0), 1)
for r in hist.to_dict("records"):
    d = wk.loc[wk["week"] <= YEAR_END_WEEK.get(r["as_of"], 0), "period_date"]
    if len(d):
        x, color = d.iloc[-1], LABEL_COLORS[r["label"]]
        fig.add_vline(x=x, line=dict(color=color, width=1.5, dash="dot"))
        fig.add_trace(go.Scatter(                      # a hoverable dot at the top of each year-end line
            x=[x], y=[ymax * 1.08], mode="markers+text", text=[f"{r['as_of']}: {LABEL_WORDS[r['label']]}"],
            textposition="middle left", textfont=dict(color=color, size=11),
            marker=dict(color=color, size=11), showlegend=False,
            hovertemplate=hover_text(r, color, cat_l)), row=1, col=1)
fig.update_layout(height=540, margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.08),
                  plot_bgcolor="white", paper_bgcolor="white", hovermode="closest",
                  hoverlabel=dict(bgcolor="white", font_size=13, align="left", namelength=-1))
fig.update_yaxes(rangemode="tozero", gridcolor="#F3F4F6")
st.plotly_chart(fig, width="stretch")
st.caption("Thin line = each week. Thick line = 13-week average, the view the labels are read from. "
           "Hover the dot at the top of a year-end line for that year's scorecard.")


# ---- step through one year's label, line by line ------------------------------------------
def walkthrough(r, wk, cat):
    """The math behind one year-end label, recomputed from the weekly rows so every number can be checked."""
    W = YEAR_END_WEEK[r["as_of"]]
    c = wk.set_index("week")["cases"]
    a = wk.set_index("week")["store_coverage"]
    this_c, last_c = c.loc[W - 51:W].sum(), c.loc[W - 103:W - 52].sum()
    this_a, last_a = a.loc[W - 51:W].mean(), a.loc[W - 103:W - 52].mean()
    q13_c, best_c = c.loc[W - 12:W].mean(), c.loc[:W].rolling(13, min_periods=1).mean().max()
    q13_a, best_a = a.loc[W - 12:W].mean(), a.loc[:W].rolling(13, min_periods=1).mean().max()
    sb, st_, tr = r["sales_vs_best"], r["stores_vs_best"], r["store_trend"]
    tr_shown = "n/a (no prior year, treated as flat)" if pd.isna(tr) else times(tr)
    tr = 1.0 if pd.isna(tr) else tr
    yes, no = "**Yes**", "no"
    q1 = (sb < 0.10) and (st_ < 0.10)
    q2 = (sb >= 0.80) and (tr >= 1.03)
    q3 = any(decline_fired(r))          # same boundary handling as everywhere else (stored numbers are rounded)

    st.markdown(f"**1. The numbers, from the weekly rows (week {W} is the end of {r['as_of']})**")
    st.markdown(f"""
| Number | How it is calculated | For this brand | Result |
|---|---|---|---|
| Sales vs its best | average weekly cases, last 13 weeks ÷ the best 13-week average the brand ever had | {q13_c:,.1f} ÷ {best_c:,.1f} | **{sb:.0%}** |
| Sales vs a year ago | cases this year ÷ cases last year | {this_c:,.0f} ÷ {last_c:,.0f} | **{change(r['sales_growth'])}** |
| Shelf vs its best | average %ACV, last 13 weeks ÷ the best 13-week average %ACV ever | {q13_a:.2f} ÷ {best_a:.2f} | **{st_:.0%}** |
| Shelf vs a year ago | average %ACV this year ÷ average %ACV last year | {this_a:.2f} ÷ {last_a:.2f} | **{tr_shown}** |
""")
    st.markdown("**2. The three questions, in order. The first yes decides. Sales vs a year ago is not used here.**")
    st.markdown(f"""
| Question | The test | This brand | Answer |
|---|---|---|---|
| Is it dead? | BOTH: sales vs best under 10% **and** shelf vs best under 10% | {sb:.0%} and {st_:.0%} | {yes + " → Discontinued" if q1 else no} |
| Is it on fire? | BOTH: sales vs best 80% or more **and** shelf up 3% or more vs a year ago | {sb:.0%} and {tr_shown} | {yes + " → Growing" if (q2 and not q1) else no} |
| Is it slipping off shelves? | EITHER: shelf down 10% or more vs a year ago **or** shelf vs best under 40% | {tr_shown} or {st_:.0%} | {yes + " → Declining" if (q3 and not q1 and not q2) else no} |
""")
    if not (q1 or q2 or q3):
        st.markdown("Yes to none → **Stable**.")
    st.markdown(f"Label at the end of {r['as_of']}: **{LABEL_WORDS[r['label']]}** ({LABEL_GLOSS[r['label']]}).")

    if pd.notna(r.get("category_growth")):
        g, cs = r["category_growth"], r.get("category_shelf_trend")
        st.markdown(f"**3. Against {cat}: the established brands in the category (two full years of history, 250+ cases in the year before this year-end)**")
        st.markdown(f"""
| | This brand | {cat.title()} | Brand ÷ category | Reading |
|---|---|---|---|---|
| Sales vs a year ago | {change(r['sales_growth'])} | {change(g)} | {times(r['vs_category'])} | {verdict(r['vs_category'])} |
| Shelf vs a year ago | {change(r['store_trend'])} | {change(cs)} | {times(r.get('vs_shelf'))} | {verdict(r.get('vs_shelf'))} |
""")
        st.caption("The category comparison does not change the label. The model sees the sales comparison as an input; "
                   "both are here so a person can judge the brand against its field.")
        if r["label"] == "decline" and r["sales_growth"] > 1 and tr < 0.90:
            st.info(f"**Sales up but labeled Declining?** Both are true. The label is about shelf: averaged over the whole year the "
                    f"brand was in {1 - tr:.0%} fewer stores than the year before (see the dip in the green line). Cases still rose "
                    f"{change(r['sales_growth'])}, so each store that kept it sold more. The model sees both and sets the chances from all of it.")


with st.expander("Step through a year's label: the math, line by line", expanded=False):
    years = [int(y) for y in hist["as_of"]]
    if years:
        pick_year = st.radio("Year-end", years, index=len(years) - 1, horizontal=True, label_visibility="collapsed")
        walkthrough(hist[hist["as_of"] == pick_year].iloc[0], wk, cat_l)
        st.caption("Shelf does most of the work. Sales only matter for the two extremes (dead, on fire). "
                   "This is how the brands were labeled by hand, and the rules copy it.")
    else:
        st.caption("No label yet: a brand needs a year of history.")

# ---- the label at each year-end, and the rest of the family -----------------------------
left, right = st.columns(2)
with left:
    st.markdown("#### Label at each year-end")
    strip = "  →  ".join(f"{r.as_of} {label_chip(r.label)}" for r in hist.itertuples())
    st.markdown(strip or "No history yet", unsafe_allow_html=True)
    for r in hist.to_dict("records"):
        st.caption(year_line(r, cat_l))
    st.caption("A brand needs a year of history before it gets its first label.")
with right:
    sibs = p[(p["family"].astype(str) == str(row["family"])) & (p["brand"] != brand)]
    st.markdown(f"#### Other lines in the {row['family']} family ({len(sibs)})")
    if len(sibs):
        m = sibs[["brand", "cases_last_year", "label", "chance_growing_next_year"]].sort_values("cases_last_year", ascending=False).copy()
        m["label"] = m["label"].map(LABEL_WORDS)
        m.columns = ["Brand", f"Cases {year}", "Label today", "Growing"]
        st.dataframe(m, hide_index=True, height=min(260, 40 + 35 * len(m)), column_config={
            f"Cases {year}": st.column_config.NumberColumn(format="localized"),
            "Growing": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1)})
    else:
        st.caption("This is the only line in its family.")

sidebar_watchlist()
footer()
