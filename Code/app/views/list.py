"""The List: every scored brand above the floor, ranked, with filters."""

import io

import pandas as pd
import streamlit as st

from common import GLOSS_LINE, LABEL_WORDS, explain, footer, header, load_labels, load_predictions, sidebar_controls, sidebar_watchlist, why_label

header("The List")
floor = sidebar_controls()
p = load_predictions()
year = int(p["as_of"].iloc[0])
if "years_of_data" not in p.columns:
    st.error("The data files are from an older build. From the Code folder run:  python app\\build_app_data.py  "
             "then restart the app.")
    st.stop()

explain("The list", f"""
One row per brand that sold at least **{floor} cases** in {year} (the size floor in the sidebar).

- **Label today**: what the brand is at the end of {year}, by the same rules a human used. The labels are about shelf space more than sales: {GLOSS_LINE}.
- **Viable {year + 1}** and **Growing {year + 1}**: the model's chance, 0 to 1, that the brand will still be viable / be growing a year from now.
  Read 0.65 as "about 65 in 100 brands that looked like this one went on to grow." Growing is part of viable, so viable is never the smaller number (two separate models; where growing comes out higher, viable is lifted to match).
- **Comes and goes** (filter): brands with half a year or more of no sales somewhere in their history, usually seasonal items, limited runs or relaunches. Their numbers measure a calendar, not a trend; the checkbox hides them.
- **Years of data**: how long the brand has been in the data. A brand with two years can look "at its best" just because there is little history behind it; the filter on the left lets you require more.
- **Sales vs category** and **Shelf vs category**: the brand's change over the year divided by its category's change (established brands only). 1.00 = moved with the category, 1.20 = did 20% better, 0.85 = lost ground. Added at Eurpac's request; the models see the sales one.
- **Why this label**: what the label means and the one number that decided it, e.g. "lost shelf space: shelf 20% of its best". Sales vs best = cases last quarter as a share of the brand's best quarter ever.
  Stores vs best = store coverage now as a share of the most it ever had. Store count = coverage this year vs last year.
- **Rank by "beating its category"** sorts on Sales vs category, highest first. The size floor only hides brands; it does
  not change the category a brand is compared with.

Filter on the left, sort with "Rank by," click a row to open that brand, pin brands to the watchlist, or download the list.
""")

# ---- filters -----------------------------------------------------------------
# Streamlit forgets a page's widgets when you leave the page. Each filter starts from the value
# saved in session_state and saves itself back, so the filters survive a trip to another page.
RANKS = ["chance of growing", "chance of viable", "cases last year", "beating its category"]
f = st.session_state.setdefault("list_filters", dict(
    cats=[], tiers=[], labels=[], min_years=1, min_grow=0.0, min_viab=0.0, search="", sort_by=RANKS[0], top_n=10,
    hide_gaps=False))
with st.sidebar:
    st.markdown("## Filters")
    cats = sorted(p["category"].astype(str).unique())
    f["cats"] = st.multiselect("Category", cats, default=[c for c in f["cats"] if c in cats], placeholder="All categories")
    tiers = [t for t in ["VALUE", "MID", "PREMIUM", "SUPER PREM", "ULTRA", "LUXURY"] if t in set(p["price_tier"].astype(str))]
    tiers += sorted(set(p["price_tier"].astype(str)) - set(tiers))
    f["tiers"] = st.multiselect("Price tier", tiers, default=[t for t in f["tiers"] if t in tiers], placeholder="All tiers")
    f["labels"] = st.multiselect("Label today", list(LABEL_WORDS), default=f["labels"], format_func=LABEL_WORDS.get,
                                 placeholder="All labels")
    f["min_years"] = st.select_slider("Years of data at least", options=[1, 2, 3, 4, 5], value=f["min_years"],
                                      help="How many years the brand has been in the data. Young brands can look like they are "
                                           "'at their best' simply because there is little history to compare against.")
    f["min_viab"] = st.slider(f"Chance viable {year + 1} at least", 0.0, 1.0, f["min_viab"], 0.05,
                              help="Start here: keep the brands that will still be worth carrying")
    f["min_grow"] = st.slider(f"Chance growing {year + 1} at least", 0.0, 1.0, f["min_grow"], 0.05,
                              help="Then: of those, which will take off")
    f["search"] = st.text_input("Search", value=f["search"], placeholder="brand or family name")
    if "comes_and_goes" in p.columns:
        f["hide_gaps"] = st.checkbox("Hide brands that come and go", value=f["hide_gaps"],
                                     help="Seasonal items, limited runs and relaunches: brands with half a year or more of no sales "
                                          "somewhere in their history. Their 'vs best' and 'vs a year ago' numbers measure a calendar, not a trend.")
    f["sort_by"] = st.radio("Rank by", RANKS, index=RANKS.index(f["sort_by"]))
    st.markdown("## Pin")
    c_n, c_b = st.columns([1, 2])
    f["top_n"] = c_n.number_input("Top", 1, 100, f["top_n"], label_visibility="collapsed")
    pin_clicked = c_b.button("Pin top N to watchlist", width="stretch",
                             help="Adds the top N of the current ranking to the watchlist")
picked, picked_tiers, labels_today = f["cats"], f["tiers"], f["labels"]
min_years, min_grow, min_viab, search, sort_by, top_n = (f["min_years"], f["min_grow"], f["min_viab"],
                                                         f["search"], f["sort_by"], f["top_n"])

view = p[(p["cases_last_year"] >= floor)].dropna(subset=["chance_growing_next_year"])
if picked:
    view = view[view["category"].astype(str).isin(picked)]
if picked_tiers:
    view = view[view["price_tier"].astype(str).isin(picked_tiers)]
if labels_today:
    view = view[view["label"].isin(labels_today)]
view = view[(view["chance_growing_next_year"] >= min_grow) & (view["chance_viable_next_year"] >= min_viab)
            & (view["years_of_data"] >= min_years)]
if f["hide_gaps"] and "comes_and_goes" in view.columns:
    view = view[~view["comes_and_goes"]]
if search:
    s = search.upper()
    view = view[view["brand"].str.upper().str.contains(s, regex=False)
                | view["family"].astype(str).str.upper().str.contains(s, regex=False)]
sort_col = {"chance of growing": "chance_growing_next_year", "chance of viable": "chance_viable_next_year",
            "cases last year": "cases_last_year", "beating its category": "vs_category"}[sort_by]
view = view.sort_values(sort_col, ascending=False, na_position="last").reset_index(drop=True)

# ---- the table ---------------------------------------------------------------
a, c = st.columns([4, 1])
a.markdown(f"**{len(view):,} brands** at a {floor}-case floor, ranked by **{sort_by}** for {year + 1}. "
           f"Click a row to open that brand.")
if pin_clicked:
    for name in view["brand"].head(int(top_n)):
        if name not in st.session_state["watch"]:
            st.session_state["watch"].append(name)
    st.rerun()
has_cat = "vs_category" in view.columns
has_shelf = "vs_shelf" in view.columns
cat_cols = (["vs_category"] if has_cat else []) + (["vs_shelf"] if has_shelf else [])
show = view[["brand", "category", "price_tier", "cases_last_year", "years_of_data", "label",
             "chance_viable_next_year", "chance_growing_next_year"] + cat_cols + ["reason"]].copy()
nums = load_labels().query("as_of == @year").set_index("brand")[["sales_vs_best", "stores_vs_best", "store_trend", "label"]]
nums = nums.reindex(show["brand"])
show["reason"] = [why_label(r) for r in nums.to_dict("records")]   # gloss, then the number that decided it
show.insert(0, "#", range(1, len(show) + 1))
show["label"] = show["label"].map(LABEL_WORDS)
show.columns = ["#", "Brand", "Category", "Price tier", f"Cases {year}", "Years of data", "Label today",
                f"Viable {year + 1}", f"Growing {year + 1}"] + (["Sales vs category"] if has_cat else []) \
               + (["Shelf vs category"] if has_shelf else []) + ["Why this label"]

picked_row = st.dataframe(
    show, hide_index=True, height=520, on_select="rerun", selection_mode="single-row",
    column_config={
        "#": st.column_config.NumberColumn(width=55, help="Position in this ranking"),
        "Brand": st.column_config.TextColumn(width=240, help="Brand extension: one line under a brand family"),
        "Category": st.column_config.TextColumn(width=175, help="NIQ spirits category"),
        "Price tier": st.column_config.TextColumn(width=110, help="NIQ price tier, value to luxury"),
        f"Cases {year}": st.column_config.NumberColumn(format="localized", width=100, help=f"9-liter cases sold in {year}"),
        "Years of data": st.column_config.NumberColumn(format="%.1f", width=115,
                                                      help="Years since the brand first appeared in the data. Under 2 means its 'best ever' is a short history"),
        "Label today": st.column_config.TextColumn(width=115, help=f"At the end of {year}. {GLOSS_LINE}"),
        f"Viable {year + 1}": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1, width=120,
                                                             help=f"Model's chance the brand is stable or growing at the end of {year + 1}"),
        f"Growing {year + 1}": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1, width=125,
                                                              help=f"Model's chance the brand is growing at the end of {year + 1}. Growing is part of viable, so this is the smaller number"),
        "Sales vs category": st.column_config.NumberColumn(format="%.2f", width=110,
                                                           help=f"The brand's sales change in {year} divided by its category's. 1.00 = moved with the category, "
                                                                "1.20 = grew 20% faster than it, 0.85 = lost ground. A very large number means the brand sold "
                                                                "almost nothing the year before. The category means its established brands: two full years of history, 250+ cases a year earlier"),
        "Shelf vs category": st.column_config.NumberColumn(format="%.2f", width=110,
                                                           help=f"The brand's store-count change in {year} divided by its category's. 1.00 = moved with the category, "
                                                                "1.10 = held shelf 10% better than it, 0.85 = lost shelf faster. Same established-brand baseline"),
        "Why this label": st.column_config.TextColumn(width=420, help="What the label means, then the number that decided it. "
                                                                        "Shelf = share of stores carrying the brand. Full math on the How Labels Work page"),
    },
)
rows = picked_row.selection.rows if picked_row and picked_row.selection else []
if rows:
    st.session_state["brand"] = view.iloc[rows[0]]["brand"]
    st.switch_page("views/brand.py")

try:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        show.to_excel(xl, sheet_name="brands", index=False)
    c.download_button("Download as Excel", buf.getvalue(), f"brand_radar_{year + 1}_floor{floor}.xlsx",
                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
except ImportError:
    c.download_button("Download as CSV", show.to_csv(index=False).encode(), f"brand_radar_{year + 1}_floor{floor}.csv",
                      "text/csv", width="stretch", help="pip install openpyxl for Excel")

# ---- top 10 per category -----------------------------------------------------
st.markdown(f"### Top 10 in each category, by {sort_by}")
st.caption("Same filters as the table above, so a category shows fewer than 10 when fewer brands pass them.")
top = view.groupby("category", observed=True).head(10)
cat_names = [c_ for c_ in cats if c_ in set(top["category"].astype(str))]
if cat_names:
    tabs = st.tabs([c_.title() for c_ in cat_names])
    for tab, cat in zip(tabs, cat_names):
        grp = top[top["category"].astype(str) == cat]
        mini = grp[["brand", "cases_last_year", "label", "chance_viable_next_year", "chance_growing_next_year"]].copy()
        mini["label"] = mini["label"].map(LABEL_WORDS)
        mini.columns = ["Brand", f"Cases {year}", "Label today", "Viable", "Growing"]
        tab.dataframe(mini, hide_index=True, column_config={
            f"Cases {year}": st.column_config.NumberColumn(format="localized"),
            "Viable": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
            "Growing": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1)})

sidebar_watchlist()
footer()
