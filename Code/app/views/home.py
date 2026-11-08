"""Home: the numbers at a glance and where to go."""

import streamlit as st

from common import GLOSS_LINE, explain, footer, header, load_predictions, sidebar_controls, sidebar_watchlist

header("Home")
floor = sidebar_controls()
p = load_predictions()
year = int(p["as_of"].iloc[0])
scored = p[(p["cases_last_year"] >= floor) & p["chance_growing_next_year"].notna()]

explain("The home page", f"""
Every spirits brand extension in NIQ's Total US Liquor Open State market gets a **label today**
(discontinued, declining, stable or growing), the way Kristin Henderson labeled brands by hand
(the labels are about shelf space more than sales: {GLOSS_LINE}),
plus two **chances for {year + 1}**: will it still be viable (stable or growing), and will it be growing.

The four numbers below follow the **size floor** in the sidebar: brands that sold fewer cases than
the floor last year are left out here and on The List (you can still open any brand's own page). Move the slider and the numbers update.
""")

c1, c2, c3, c4 = st.columns(4)
for col, num, text, tip in [
    (c1, f"{len(p):,}", "brands labeled", "Every brand with at least a year of history, regardless of size"),
    (c2, f"{len(scored):,}", f"brands above the {floor}-case floor", "What the List page shows at this floor"),
    (c3, f"{(scored['label'] == 'growing').mean():.0%}", "growing today", "Share of those brands labeled growing at the end of the data"),
    (c4, f"{scored['viable'].mean():.0%}", "viable today", "Share labeled stable or growing"),
]:
    col.markdown(f'<div class="card" title="{tip}"><div class="big">{num}</div><div class="big-label">{text}</div></div>',
                 unsafe_allow_html=True)

st.markdown("")
st.markdown(f"""
**Where to go**

- **The List**: every brand above the floor, ranked. Filter by category, price tier, label, or how sure the model is. Search. Pin to a watchlist. Export.
- **One Brand**: a brand's sales-and-shelf scorecard, its weekly chart, its label at every year-end, and both chances.
- **How Labels Work**: the reference page. Every number, the three questions, worked examples, the category context.
- **The Model**: how the predictions held up on a year the models never saw, what they lean on, and how to read a chance.

Data runs to the end of {year}. A brand needs a year of history to get a label and two years to get a chance.
""")

sidebar_watchlist()
footer()
