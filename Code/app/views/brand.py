"""One brand: its chart, its label at every year-end, and why it got its score."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from common import (EURPAC_BLUE, LABEL_COLORS, LABEL_WORDS, current_floor, explain, footer, header, label_chip,
                    load_labels, load_predictions, load_weekly, sidebar_watchlist, with_category_context)

header("One Brand")
floor = current_floor()


def store_change(tr):
    """Store coverage this year vs last, in words. The rules treat a missing trend (no stores last year)
    as flat, so this does too. A tenfold jump means it was in almost no stores a year ago; a percent
    like +5000% says nothing useful, so it gets words instead."""
    if pd.isna(tr):
        tr = 1.0
    if tr >= 10:
        return "far more stores than a year ago (it was in almost none)"
    return f"{tr - 1:+.0%} stores vs a year ago"


def why_lines(r):
    """Which question got a yes, then the numbers behind it, as short lines. Same order as the rules."""
    sb, st_, tr = r["sales_vs_best"], r["stores_vs_best"], r["store_trend"]
    if pd.isna(sb) or pd.isna(st_):
        return ["No sales or store coverage on record, so there is no best to compare against."]
    if r["label"] == "discontinued":
        return ["Dead.", f"Sales at {sb:.0%} of its best", f"and in only {st_:.0%} of the stores it once had."]
    if r["label"] == "growing":
        return ["On fire.", f"Selling at {sb:.0%} of its best", f"and in {store_change(tr)}."]
    if r["label"] == "decline":
        lines = ["Slipping off shelves."]
        if not pd.isna(tr) and tr < 0.90:
            lines.append(f"In {1 - tr:.0%} fewer stores than a year ago.")
        if st_ < 0.40:
            lines.append(f"In only {st_:.0%} of the stores it once had.")
        return lines
    return ["Not dead, not on fire, not slipping.", f"Selling at {sb:.0%} of its best,",
            f"in {st_:.0%} of the stores it once had,", f"and in {store_change(tr)}."]


def why(r):
    """The same thing as one sentence, for captions."""
    return " ".join(why_lines(r))


p, labels, weekly = with_category_context(load_predictions(), floor), load_labels(), load_weekly()
year = int(p["as_of"].iloc[0])
YEAR_END_WEEK = {2022: 104, 2023: 156, 2024: 208, 2025: 260, 2026: 312, 2027: 364}

explain("One brand", f"""
This is the picture a person used to label brands by hand: **cases sold each week** (blue) and
**store coverage** (green, %ACV: the share of the market's stores that carry it, weighted by store size).
The thin line is each week; the thick line is the 13-week average the labels are read from.

Each year-end we ask three questions: **is it dead, is it on fire, is it losing shelf space.**
Yes to one gives the label (Discontinued, Growing, Declining). Yes to none means Stable.
Hover a dot at the top of a year-end line, or read the list under the chart, to see which answer it got.
The two chances at the top are the model's guess for {year + 1}.
""")

# ---- pick a brand -------------------------------------------------------------
names = p.sort_values("cases_last_year", ascending=False)["brand"].tolist()
default = st.session_state.get("brand", names[0])
c_pick, c_pin = st.columns([5, 1])
brand = c_pick.selectbox("Brand", names, index=names.index(default) if default in names else 0,
                         help="Type to search. Sorted by size.")
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
last = hist.iloc[-1] if len(hist) else None

# ---- header card --------------------------------------------------------------
c1, c2, c3, c4 = st.columns([3, 1.2, 1.2, 1.2])
with c1:
    st.markdown(f"### {brand}")
    st.markdown(f"{row['family']} · {cat} · {row['price_tier']}")
    st.markdown(f"Label today: {label_chip(row['label'])}", unsafe_allow_html=True)
    st.markdown(f'<div class="reason">{why(last) if last is not None else row["reason"]}</div>', unsafe_allow_html=True)
    if pd.notna(row["vs_category"]):
        verdict = "beating" if row["vs_category"] > 0 else "trailing"
        st.caption(f"Cases {row['case_growth']:+.0f}% vs {year - 1}; the {cat.title()} category {row['category_growth']:+.0f}% "
                   f"(extensions with {floor}+ cases). "
                   f"**{verdict.capitalize()} its category by {abs(row['vs_category']):.0f} pts.**")
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
if not scored:
    st.info("Below the 12-case scoring floor, so no chance is given. The label and chart still apply.")
elif row["cases_last_year"] < floor:
    st.info(f"This brand is below your {floor}-case floor, so it is hidden on the List page. Shown here because you asked for it.")

# ---- the chart (Kristin's view) -------------------------------------------------
overlay = st.toggle(f"Overlay the {cat.title()} category average (scaled)", value=False,
                    help="The category's average brand, scaled to this brand's size, so you can see whether the brand or the whole category is moving")
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                    subplot_titles=("Cases per week", "Store coverage (%ACV)"))
fig.add_trace(go.Scatter(x=wk["period_date"], y=wk["cases"], name="cases, weekly", hoverinfo="skip",
                         line=dict(color="#93C5FD", width=1), opacity=0.7), row=1, col=1)
fig.add_trace(go.Scatter(x=wk["period_date"], y=wk["cases"].rolling(13).mean(), name="cases, 13-week average",
                         hovertemplate="%{x|%b %d, %Y}<br>%{y:,.1f} cases a week (13-week average)<extra></extra>",
                         line=dict(color=EURPAC_BLUE, width=2.5)), row=1, col=1)
fig.add_trace(go.Scatter(x=wk["period_date"], y=wk["store_coverage"], name="coverage, weekly", hoverinfo="skip",
                         line=dict(color="#86EFAC", width=1), opacity=0.7), row=2, col=1)
fig.add_trace(go.Scatter(x=wk["period_date"], y=wk["store_coverage"].rolling(13).mean(), name="coverage, 13-week average",
                         hovertemplate="%{x|%b %d, %Y}<br>%ACV %{y:.0f} (13-week average)<extra></extra>",
                         line=dict(color="#15803D", width=2.5)), row=2, col=1)
if overlay:
    cat_brands = p.loc[p["category"].astype(str) == cat, "brand"]
    cat_wk = (weekly[weekly["brand"].isin(cat_brands)].groupby("period_date")[["cases", "store_coverage"]].mean())
    for col_, r_, color in (("cases", 1, "#9CA3AF"), ("store_coverage", 2, "#9CA3AF")):
        own = wk.set_index("period_date")[col_].rolling(13).mean()
        ref = cat_wk[col_].rolling(13).mean()
        scale = (own.mean() / ref.mean()) if ref.mean() else 1
        fig.add_trace(go.Scatter(x=ref.index, y=ref * scale, name=f"{cat.title()} average (scaled)", hoverinfo="skip",
                                 line=dict(color=color, width=2, dash="dash"), showlegend=(r_ == 1)), row=r_, col=1)
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
            hovertemplate=(f"<b>End of {r['as_of']}: {LABEL_WORDS[r['label']]}</b><br>"
                           + "<br>".join(why_lines(r)) + "<extra></extra>")), row=1, col=1)
fig.update_layout(height=540, margin=dict(l=10, r=10, t=40, b=10), legend=dict(orientation="h", y=-0.08),
                  plot_bgcolor="white", paper_bgcolor="white", hovermode="closest",
                  hoverlabel=dict(bgcolor="white", font_size=13, align="left", namelength=-1))
fig.update_yaxes(rangemode="tozero", gridcolor="#F3F4F6")
st.plotly_chart(fig, width="stretch")
st.caption("Thin line = each week. Thick line = 13-week average, the view the labels are read from. "
           "Hover the dot at the top of a year-end line to see why the brand got that label.")

# ---- the label at each year-end, and the rest of the family -----------------------------
left, right = st.columns(2)
with left:
    st.markdown("#### Label at each year-end")
    strip = "  →  ".join(f"{r.as_of} {label_chip(r.label)}" for r in hist.itertuples())
    st.markdown(strip or "No history yet", unsafe_allow_html=True)
    for r in hist.to_dict("records"):
        st.caption(f"**{r['as_of']} {LABEL_WORDS[r['label']]}**: {why(r)}")
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

# ---- how a label is decided, tucked away for whoever wants it ----------------------------
with st.expander("How a label is decided: three yes/no questions, in order", expanded=False):
    st.markdown("""
1. **Is it dead?** Sales almost nothing *and* almost no stores carry it (both under 10% of its best). → **Discontinued**
2. **Is it on fire?** Selling about as well as it ever has (80%+ of its best) *and* in more stores than a year ago. → **Growing**
3. **Is it slipping off shelves?** In fewer stores than a year ago (down 10%+), *or* in way fewer stores than it once was (under 40% of its best). → **Declining**

Yes to none of the three → **Stable**. Nothing dramatic is happening.

The green line does most of the work. Sales only matter for the two extremes.
""")
    if last is not None and not (pd.isna(last["sales_vs_best"]) or pd.isna(last["stores_vs_best"])):
        trend = last["store_trend"]
        trend = ("n/a (no stores a year ago; the rules count it as flat)" if pd.isna(trend)
                 else "10+ (was in almost no stores)" if trend >= 10 else f"{trend:.2f}")
        st.markdown(f"""
**{brand} today, the three numbers the questions use**

| | | |
|---|---|---|
| Sales vs best | **{last['sales_vs_best']:.0%}** | cases in the last quarter, as a share of the best quarter ever |
| Stores vs best | **{last['stores_vs_best']:.0%}** | store coverage now, as a share of the most it ever had |
| Store trend | **{trend}** | coverage this year / last year (above 1 = more stores) |
""")

sidebar_watchlist()
footer()
