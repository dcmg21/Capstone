"""
STEP 1: Load the data.

Starts from NIQ's raw feed and does our own prep:
    keep spirits, keep one market, add week (1-260), period_date, and year.

Run the whole file (Ctrl+Shift+Enter). You get:
    sales   one row per product (UPC) per week, about 7.3 million rows
    guide   what every column means (open it in the Data Explorer)
    check   our data vs Kristin's prepared file. All "same" = True means we match.
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.dataset as ds
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config

MEGACATEGORY = "TOTAL SPIRITS"
MARKET = "Total US Liquor Open State"

# NIQ = straight from NIQ's feed. OURS = we add it in load_sales().
GUIDE = {
    "UPC": ("NIQ", "Barcode for one product in one size. The smallest unit."),
    "ITEM": ("NIQ", "Full product description: brand, proof, size, packaging."),
    "BRAND OWNER": ("NIQ", "Corporate parent that owns the brand."),
    "ALC MANUFACTURER": ("NIQ", "Company that makes it. Can differ from the owner."),
    "BRAND HIGH": ("NIQ", "NIQ's master brand name."),
    "BRAND LOW": ("NIQ", "NIQ's sub-brand name."),
    "ALC BRAND FAMILY": ("NIQ", "The brand a shopper knows, e.g. OLD FORESTER."),
    "ALC BRAND EXTENSION": ("NIQ", "A line under the family, e.g. OLD FORESTER 1897. THE UNIT WE ANALYZE."),
    "ALC CATEGORY": ("NIQ", "Spirit type: VODKA, WHISKEY, TEQUILA..."),
    "ALC SUBCATEGORY": ("NIQ", "Finer type within the category."),
    "ALC SPIRITS PRICE TIER": ("NIQ", "VALUE, MID, PREMIUM, SUPER PREM, ULTRA, LUXURY."),
    "$": ("NIQ", "Dollar sales that week. About 1 in 5 rows is $0."),
    "Base $": ("NIQ", "Dollars NIQ expects with no promotion."),
    "Incr $": ("NIQ", "$ minus Base $. Can be negative."),
    "Units": ("NIQ", "Bottles/cans/packs sold."),
    "Base Units": ("NIQ", "Units NIQ expects with no promotion."),
    "Incr Units": ("NIQ", "Units minus Base Units."),
    "Case": ("NIQ", "Standard cases sold (likely 9L = 12 x 750ml, confirm). OUR SALES MEASURE."),
    "Base Case": ("NIQ", "Cases NIQ expects with no promotion."),
    "Incr Case": ("NIQ", "Case minus Base Case."),
    "Avg Unit Price": ("NIQ", "$ / Units. Blank when nothing sold."),
    "Base Unit Price": ("NIQ", "Everyday price per unit."),
    "Any Promo Unit Price": ("NIQ", "Price per unit on promotion. Blank = no promotion."),
    "No Promo Unit Price": ("NIQ", "Price per unit not on promotion."),
    "%ACV": ("NIQ", "How widely stocked, 0-100 (share of stores, weighted by store size)."),
    "$ Shr - ALC MEGACATEGORY": ("NIQ", "This item's share of all spirits dollars that week."),
    "week": ("OURS", "1 to 260. 1 = week ending 23 Jan 2021."),
    "period_date": ("OURS", "Week-ending Saturday, read from NIQ's 'Period Description'."),
    "year": ("OURS", "52-week year starting late January: 2021 to 2025."),
}
DROPPED = ["Market Description", "ALC MEGACATEGORY", "Period Description"]  # one value each after filtering


def load_sales(columns=None):
    """Spirits in one market, plus week, period_date, year. `columns` limits what is read."""
    config.check()
    t0 = time.time()
    raw = ds.dataset(config.RAW_ALL, format="parquet")
    wanted = raw.schema.names if columns is None else [c for c in columns if c in raw.schema.names]
    keep = (pc.field("ALC MEGACATEGORY") == MEGACATEGORY) & (pc.field("Market Description") == MARKET)
    table = raw.to_table(columns=list(dict.fromkeys([*wanted, "Period Description"])), filter=keep)
    df = table.to_pandas(strings_to_categorical=True, split_blocks=True, self_destruct=True)

    # "1 w/e 01/23/21" -> date -> week number
    texts = df["Period Description"].cat.categories
    dates = pd.to_datetime(pd.Series(texts).str.extract(r"(\d{1,2}/\d{1,2}/\d{2})")[0], format="%m/%d/%y")
    week_of = {d: i + 1 for i, d in enumerate(sorted(dates.unique()))}
    df["period_date"] = df["Period Description"].map(dict(zip(texts, dates))).astype("datetime64[ns]")
    df["week"] = df["Period Description"].map({t: week_of[d] for t, d in zip(texts, dates)}).astype("int16")
    df["year"] = ((df["week"] - 1) // 52 + 2021).astype("int16")
    df = df.drop(columns=[c for c in DROPPED if c in df.columns])

    print(f"Loaded {len(df):,} rows x {df.shape[1]} columns in {time.time() - t0:.0f}s "
          f"({df['period_date'].min():%d %b %Y} to {df['period_date'].max():%d %b %Y})")
    return df


def column_guide(df):
    rows = []
    for col in df.columns:
        source, meaning = GUIDE.get(col, ("?", "not documented"))
        s = df[col]
        if isinstance(s.dtype, pd.CategoricalDtype):
            values = f"{s.nunique():,} distinct"
        elif pd.api.types.is_datetime64_any_dtype(s):
            values = f"{s.min():%d %b %Y} to {s.max():%d %b %Y}"
        else:
            values = f"min {s.min():,.2f} | median {s.median():,.2f} | max {s.max():,.2f}"
        rows.append({"column": col, "source": source, "meaning": meaning,
                     "values": values, "missing_pct": round(100 * s.isna().mean(), 1)})
    return pd.DataFrame(rows)


def check_against_kristin(df):
    """Same rows, weeks, products, brands, cases, dollars, and cases in every week?"""
    need = ["UPC", "ALC BRAND EXTENSION", "week", "Case", "$"]
    if not set(need) <= set(df.columns) or not config.KRISTIN_FILE.exists():
        print("Skipping check (columns not loaded or Kristin's file missing).")
        return None
    hers = pq.read_table(config.KRISTIN_FILE, columns=need).to_pandas()

    def totals(d):
        return {"rows": len(d), "weeks": d["week"].nunique(), "UPCs": d["UPC"].nunique(),
                "brand extensions": d["ALC BRAND EXTENSION"].nunique(),
                "total cases": d["Case"].sum(), "total dollars": d["$"].sum()}

    check = pd.DataFrame({"ours": totals(df), "kristin": totals(hers)}).astype(float)
    ours_wk = df.groupby("week", observed=True)["Case"].sum().to_numpy()
    hers_wk = hers.groupby("week")["Case"].sum().sort_index().to_numpy()
    check.loc["weeks with different cases"] = [(~np.isclose(ours_wk, hers_wk)).sum(), 0]
    check["same"] = np.isclose(check["ours"], check["kristin"])
    print(check.to_string(float_format="{:,.0f}".format))
    print("MATCHES KRISTIN." if check["same"].all() else "DIFFERENT: look at rows where same = False.")
    return check


if __name__ == "__main__":
    sales = load_sales()
    guide = column_guide(sales)
    check = check_against_kristin(sales)
