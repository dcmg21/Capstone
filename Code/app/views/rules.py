"""How Labels Work: the reference page. Every number, every rule, worked examples pulled from the data."""

import pandas as pd
import streamlit as st

from common import GLOSS_LINE, current_floor, footer, header, label_chip, load_labels, sidebar_watchlist, times

header("How Labels Work")
current_floor()
labels = load_labels()
year = int(labels["as_of"].max())
latest = labels[labels["as_of"] == year].set_index("brand")


fmt_change = times   # '+41%', '-22%', or '7.6x' for a big jump


# ---- 1. what we measure ---------------------------------------------------------------
st.markdown("### 1. Two things, measured each week")
st.markdown(f"""
NIQ gives us, for every brand extension, every week: **cases sold** (9-liter cases) and **%ACV** (the share of the
market's stores that carry it, weighted by store size). We call them **sales** and **shelf**. Everything else on this
page is built from those two columns.

We smooth both with a **13-week average** (one quarter) because a single week is noisy. That smoothed line is what a
person looked at when labeling brands by hand, and it is the thick line on every brand's chart.

A week with no sales in any tracked store has zero cases and **no shelf reading** (NIQ reports %ACV only where the brand
sold), so a brand that comes and goes shows breaks in its green line, and its shelf numbers for that year rest on the
weeks it was on a shelf. That is rare above the 250-case floor (about 1 brand in 100 has large gaps) and common below it,
which is one more reason the floor exists. Brands with half a year or more of no sales somewhere in their history are
flagged **"comes and goes"** (about 3 in 100 on the List: seasonal items, limited runs, relaunches); the List can hide them.

A **year-end** is the last week of each 52-week block of data: weeks 104, 156, 208, 260 are the ends of 2022 to {year}.
A brand gets a label at each year-end it has been around for, once it has at least 52 weeks of history.
""")

# ---- 2. the four numbers ---------------------------------------------------------------
st.markdown("### 2. The four numbers behind a label")
st.markdown("""
Two for sales, two for shelf. Each compares the brand with **itself**, never with another brand.

| | Name | How it is calculated | Reads as |
|---|---|---|---|
| Sales | **Sales vs its best** | average weekly cases over the last 13 weeks ÷ the best 13-week average the brand ever had | 100% = selling as well as it ever has |
| Sales | **Sales vs a year ago** | cases in the last 52 weeks ÷ cases in the 52 weeks before that | +41% = sold 41% more than the year before |
| Shelf | **Shelf vs its best** | average %ACV over the last 13 weeks ÷ the best 13-week average %ACV it ever had | 30% = in less than a third of the stores it once reached |
| Shelf | **Shelf vs a year ago** | average %ACV over the last 52 weeks ÷ average %ACV over the 52 weeks before | -10% = in 10% fewer stores than the year before (the same thing as a ratio of 0.90) |

"Best ever" means the best quarter in the brand's whole history up to that year-end, so a young brand's "best" is a
short history, which is why the List lets you require more years of data.
""")

# ---- 3. the three questions -------------------------------------------------------------
st.markdown("### 3. The three questions, asked in order")
st.markdown("""
| | Question | The test | Yes means |
|---|---|---|---|
| 1 | **Is it dead?** | BOTH: sales vs best **under 10%** AND shelf vs best **under 10%** | **Discontinued**: gone from shelves |
| 2 | **Is it on fire?** | BOTH: sales vs best **80% or more** AND shelf **up 3% or more** vs a year ago | **Growing**: near its best and adding shelf |
| 3 | **Is it slipping off shelves?** | EITHER: shelf **down 10% or more** vs a year ago, OR shelf vs best **under 40%** | **Declining**: lost shelf space |
| | Yes to none | | **Stable**: holding its shelf |

The first yes wins. Questions 1 and 2 need both halves; question 3 needs only one. Notice what is **not** in the tests: sales vs a year ago. A brand's sales can be up and it can
still be Declining, because the label is mostly about shelf. That is on purpose. Kristin Henderson labeled 112 vodka
brands by hand from their charts, and what her eye followed was distribution. These rules reproduce her labels 90%
of the time on tier and 96% on viable / not viable.

Question 3 has two ways to say yes, and they describe two different brands:
**losing shelf right now** (down 10%+ on the year) and **lost most of its shelf and stayed there** (under 40% of its best,
even if flat this year). Both get "Declining: lost shelf space."

**Why shelf does most of the work.** When the models were tested, shelf vs best was by far the strongest predictor of
whether a brand is still viable a year later (importance 0.24; sales vs best 0.01). A brand still in most of the stores
it ever reached almost always survives. Growth is the opposite: sales vs best is the strongest predictor there.
""")


# ---- 4. worked examples, live from the data ---------------------------------------------
def example(name, title, note):
    if name not in latest.index:
        return
    r = latest.loc[name]
    tr = 1.0 if pd.isna(r["store_trend"]) else r["store_trend"]
    q1 = (r["sales_vs_best"] < 0.10) and (r["stores_vs_best"] < 0.10)
    q2 = (r["sales_vs_best"] >= 0.80) and (tr >= 1.03)
    q3 = (tr < 0.90) or (r["stores_vs_best"] < 0.40)
    yes = lambda b: "**yes**" if b else "no"
    st.markdown(f"**{title}: {name}** ({str(r['category']).lower()}, {r['cases_last_year']:,.0f} cases in {year}) "
                f"{label_chip(r['label'], gloss=True)}", unsafe_allow_html=True)
    st.markdown(f"""
| Sales vs best | Sales vs a year ago | Shelf vs best | Shelf vs a year ago | Dead? | On fire? | Slipping? |
|---|---|---|---|---|---|---|
| {r['sales_vs_best']:.0%} | {fmt_change(r['sales_growth'])} | {r['stores_vs_best']:.0%} | {fmt_change(tr)} | {yes(q1)} | {yes(q2 and not q1)} | {yes(q3 and not q1 and not q2)} |
""")
    st.caption(note)


st.markdown("### 4. Four brands, worked through")
st.caption(f"Pulled live from the end-of-{year} data. Open any of them on the One Brand page and use \"Step through\" to see the arithmetic.")
example("G4 RPSDO TEQUILA", "On fire",
        "Sales at its best and shelf more than doubled on the year: yes to question 2. The clearest kind of Growing.")
example("CHUM CHURUM SOON HARI PEACH", "Sales up, but Declining",
        "Sales at 99% of best and up on the year, but shelf is down 10.2% vs a year ago, just past the 10% line: yes to question 3 "
        "(losing shelf right now). Each store that kept it sold more. The label is about shelf; the model also sees the sales, "
        "which is why its viable chance is high.")
example("CONQUISTADOR GOLD TEQUILA", "Flat, but Declining",
        "Shelf is flat on the year (1.01), but at 30% of its best: yes to question 3 the other way (lost most of its shelf "
        "and stayed there). It is in a fraction of the stores it once reached and is not winning them back.")
example("TITO'S VODKA", "Stable",
        "Near its best, shelf steady: no to all three. The biggest brand in the data is \"nothing dramatic is happening,\" "
        "which is what Stable means.")

# ---- 5. viable, and the two chances -------------------------------------------------------
st.markdown("### 5. From four words to two questions about next year")
st.markdown(f"""
**Viable** is Kristin's word for stable or growing: the brand is healthy enough to keep. Declining or discontinued is not.
That turns the four labels into a 1 or a 0.

The models answer two yes/no questions about a year from now: **will it be viable?** and **will it be growing?**
Growing is part of viable, so the viable chance should be the bigger number. A chance of 0.65 means: of 100 brands that
looked like this one a year earlier, about 65 turned out yes. The chances are **calibrated** so that sentence is true
(the raw model scores are stretched because growing is rare; a calibration step maps them back to real rates without
changing any brand's rank).

Tested on {year}, which the models never saw while learning: 98 of the 100 brands the viable model was most sure about
were still viable; 66 of the 100 the growing model was most sure about were growing. Details on The Model page.
""")

# ---- 6. category context -------------------------------------------------------------------
st.markdown("### 6. The brand against its category")
st.markdown("""
Added in November 2026 at Eurpac's request. Two more numbers per brand, **context, not rules**: they never change a label.

| Name | How it is calculated | Reads as |
|---|---|---|
| **Category's sales vs a year ago** | add up the cases of the category's established brands this year, divide by the same brands' cases last year | cordials -5% = the field shrank 5% |
| **Category's shelf vs a year ago** | the same with average %ACV | tequila -5% = established tequilas are in 5% fewer stores |
| **Sales vs category** | brand's sales vs a year ago ÷ category's | 1.20 = grew 20% faster than its field; shown as "ahead / keeping pace / behind" |
| **Shelf vs category** | brand's shelf vs a year ago ÷ category's | 0.85 = lost shelf faster than its field |

**Established brands** means two full years of history and at least 250 cases the year before, so a brand is compared
with real competitors, not with new launches or dying 10-case brands. Big jumps show as a multiple ("7.6x" means this
year was 7.6 times last year). A very large ratio means the brand sold almost nothing the year before.

We tested both as model inputs. Neither changed the predictions (importance near zero): a brand's own history already
carries whatever its category is doing. They are on screen because a person reading the list wants them.
""")

cats = (latest.groupby(latest["category"].astype(str))[["category_growth", "category_shelf_trend"]].first()
        .dropna(how="all").sort_values("category_growth"))
if len(cats):
    st.markdown(f"**Every category's established brands, {year} vs {year - 1}**")
    st.markdown("| Category | Sales vs a year ago | Shelf vs a year ago |\n|---|---|---|\n" + "\n".join(
        f"| {c.title()} | {fmt_change(r['category_growth'])} | {fmt_change(r.get('category_shelf_trend'))} |" for c, r in cats.iterrows()))
    if cats["category_shelf_trend"].notna().any() and (cats["category_shelf_trend"].dropna() < 1).mean() > 0.8:
        st.info(f"**Shelf shrank almost everywhere in {year}.** Established brands in nearly every category were in fewer stores "
                f"than a year earlier. A brand that merely held its store count was beating its field. The models were tested in "
                f"this same market, so the chances already reflect it.")

# ---- 7. what we checked and left alone ------------------------------------------------------
st.markdown("### 7. Things we checked and chose not to change")
st.markdown("""
- **A "sales guard" on question 3** (don't call it Declining if sales are at 80%+ of best and up on the year). About 2% of
  Declining labels. Those brands do behave like Stable ones a year later, and the guard would not touch any of Kristin's
  112, but it changes the published rules, so it is parked for the team to decide. The label gloss ("lost shelf space")
  and the scorecard make the case readable without it.
- **A 500-case floor instead of 250.** Retested: not better (growing 60 of 100 vs 66), so 250 stays.
- **Shelf vs category as a rule or a model input.** Raw shelf trend predicts next year at least as well; it stays as context.
""")

st.markdown("### Words")
st.markdown(f"""
**Case**: a 9-liter case. **%ACV / shelf**: share of the market's stores carrying the brand, weighted by store size.
**13-week average**: one quarter, the smoothing a person used when labeling. **Year-end**: the last week of each 52-week block.
**Labels**: {GLOSS_LINE}. **Viable**: stable or growing. **Size floor**: cases sold last year a brand needs to be on the List;
the models were tested at 250. **Established brands**: two full years of history and 250+ cases the year before.
""")

sidebar_watchlist()
footer()
