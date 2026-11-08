"""
STEP 2: Label every brand extension the way Kristin hand-labeled vodka.

Her four labels, from her charts of cases and %ACV (13-week average, "focus on the
past 2 years"). Devin's rules turn what her eye did into three numbers per brand:

    sales_vs_best    cases in the last 13 weeks, as a share of the brand's best 13-week stretch ever
    stores_vs_best   store coverage (%ACV) now, as a share of the most it ever had
    store_trend      store coverage this year / last year  (above 1 = more stores than a year ago)

and four rules, first match wins:

    discontinued   sales_vs_best < 10%  and  stores_vs_best < 10%
    growing        sales_vs_best >= 80% and  store_trend >= 1.03
    decline        store_trend < 0.90  or  stores_vs_best < 40%
    stable         everything else

Binary, Kristin's own mapping:  viable = 1 (stable, growing)   low_performance = 0 (decline, discontinued)

"As of" a year-end: the data is cut at that week and the rules run on what existed then.
So each brand gets a label for the end of 2022, 2023, 2024 and 2025 (week 260).

Run the whole file. You get `labels`: one row per brand per year-end, with the label,
the 1/0, the three numbers, and a `reason` column that explains the label.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from step01_load_data import load_sales  # noqa: E402

BRAND = "ALC BRAND EXTENSION"
COLUMNS = [BRAND, "ALC BRAND FAMILY", "ALC CATEGORY", "ALC SPIRITS PRICE TIER", "Case", "%ACV", "$", "Units", "Incr Case"]
MA = 13            # weeks in the moving average Kristin plotted
YEAR = 52
MIN_WEEKS = 52     # need a year of history to be labeled (her filter)
YEAR_ENDS = {2022: 104, 2023: 156, 2024: 208, 2025: 260}   # last week of each 52-week year (data starts Jan 2021)


def year_ends_in(sales):
    """Every complete 52-week year in the data that has a full prior year too (so the rules have 2 years to read).
    New data = new year-ends, with no code change."""
    last = int(sales["week"].max())
    return {2020 + k: 52 * k for k in range(2, last // 52 + 1)}   # week 104 = end of 2022

RULES = dict(dead=0.10, near_peak=0.80, grow_yoy=1.03, decline_yoy=0.90, decline_peak=0.40)
TIERS = ["discontinued", "decline", "stable", "growing"]
VIABLE = ["stable", "growing"]


def weekly_tables(sales):
    """Brand x week tables: cases (sum of UPCs), %ACV (best UPC), dollars, units, promo cases.
    NaN before a brand's launch, 0 after. Returns a dict keyed by name."""
    w = sales.groupby([BRAND, "week"], observed=True).agg(
        cases=("Case", "sum"), acv=("%ACV", "max"), dollars=("$", "sum"),
        units=("Units", "sum"), promo_cases=("Incr Case", "sum"))
    w["cases"] = w["cases"].clip(lower=0)
    w["acv"] = w["acv"].fillna(0)
    out = {}
    for col in w.columns:
        wide = w[col].unstack("week").reindex(columns=range(1, sales["week"].max() + 1))
        wide.index = wide.index.astype(str)
        launched = wide.notna().cumsum(axis=1) > 0
        out[col] = wide.fillna(0).where(launched)
    return out


def features(tables, end_week):
    """The numbers per brand, using only weeks up to end_week."""
    t = {k: v.loc[:, :end_week] for k, v in tables.items()}
    c, a = t["cases"], t["acv"]

    def vs_peak(w):
        peak = w.T.rolling(MA, min_periods=1).mean().max()
        return w.iloc[:, -MA:].mean(axis=1) / peak

    def yoy(w):
        last, prev = w.iloc[:, -YEAR:].mean(axis=1), w.iloc[:, -2 * YEAR:-YEAR].mean(axis=1)
        return last / prev.replace(0, np.nan)

    def quarters_at_best(w):
        """Momentum: how many quarters in a row, counting back from now, sales were at 80%+ of the best so far."""
        ma = w.T.rolling(MA, min_periods=1).mean().T                       # 13-week average
        pts = ma.iloc[:, ::-MA].iloc[:, :8]                                # one point per quarter, newest first, last 8
        best = ma.cummax(axis=1).iloc[:, ::-MA].iloc[:, :8]                # best so far at each of those points
        return (pts >= 0.8 * best).cumprod(axis=1).sum(axis=1)             # count until the first miss

    last_year = lambda w: w.iloc[:, -YEAR:].sum(axis=1)
    f = pd.DataFrame({"weeks_of_history": c.notna().sum(axis=1),       # weeks since the brand first appeared
                      "cases_last_year": last_year(c),                   # brand size
                      "store_coverage": a.iloc[:, -MA:].mean(axis=1),    # %ACV right now
                      "sales_vs_best": vs_peak(c), "stores_vs_best": vs_peak(a),
                      "store_trend": yoy(a), "sales_growth": yoy(c),     # this year / last year
                      "price": last_year(t["dollars"]) / last_year(t["units"]).replace(0, np.nan),  # $ per unit, last year
                      "promo_share": (last_year(t["promo_cases"]) / last_year(c).replace(0, np.nan)).clip(lower=0),
                      "quarters_at_best": quarters_at_best(c)})         # promo_share = NIQ's estimate of cases sold on promotion
    return f[f["weeks_of_history"] >= MIN_WEEKS]


def apply_rules(f, dead, near_peak, grow_yoy, decline_yoy, decline_peak):
    yoy = f["store_trend"].fillna(1.0)
    label = np.select(
        [(f["sales_vs_best"] < dead) & (f["stores_vs_best"] < dead),
         (f["sales_vs_best"] >= near_peak) & (yoy >= grow_yoy),
         (yoy < decline_yoy) | (f["stores_vs_best"] < decline_peak)],
        ["discontinued", "growing", "decline"], default="stable")
    pct = lambda s: (100 * s).round().astype("Int64").astype(str) + "%"
    chg = (100 * (yoy - 1)).round().astype("Int64")
    trend = np.where(chg >= 0, "up " + chg.astype(str) + "%", "down " + (-chg).astype(str) + "%")
    trend = np.where(yoy >= 10, "up from almost none", trend)     # +5000% says nothing a reader can use
    reason = ("selling at " + pct(f["sales_vs_best"]) + " of its best; in " + pct(f["stores_vs_best"])
              + " of the stores it once had; store count " + trend + " vs last year")
    no_best = f["sales_vs_best"].isna() | f["stores_vs_best"].isna()   # never sold: no best to compare against
    reason = reason.where(~no_best, "no sales or store coverage on record")
    return label, reason


def label_all(sales, rules=RULES, year_ends=None):
    year_ends = year_ends or year_ends_in(sales)
    tables = weekly_tables(sales)
    info = (sales.groupby(BRAND, observed=True)[["ALC BRAND FAMILY", "ALC CATEGORY", "ALC SPIRITS PRICE TIER"]].first()
            .rename(index=str).rename(columns={"ALC BRAND FAMILY": "family", "ALC CATEGORY": "category",
                                               "ALC SPIRITS PRICE TIER": "price_tier"}))
    parts = []
    for year, week in year_ends.items():
        f = features(tables, week)
        f["label"], f["reason"] = apply_rules(f, **rules)
        f["viable"] = f["label"].isin(VIABLE).astype(int)
        f.insert(0, "as_of", year)
        parts.append(f)
    out = pd.concat(parts).rename_axis("brand").reset_index()
    out = out.merge(info, left_on="brand", right_index=True, how="left")
    cols = ["brand", "family", "category", "price_tier", "as_of", "label", "viable", "reason",
            "weeks_of_history", "cases_last_year", "store_coverage", "sales_vs_best", "stores_vs_best",
            "store_trend", "sales_growth", "price", "promo_share", "quarters_at_best"]
    return out[cols].round({"cases_last_year": 0, "store_coverage": 2, "sales_vs_best": 3, "stores_vs_best": 3,
                            "store_trend": 3, "sales_growth": 3, "price": 2, "promo_share": 3})


if __name__ == "__main__":
    sales = load_sales(columns=COLUMNS)
    labels = label_all(sales)
    print(pd.crosstab(labels["as_of"], labels["label"], margins=True))
    print("\nshare viable by year-end  (viable = Kristin's word for stable or growing = the 1):")
    print(labels.groupby("as_of")["viable"].mean().round(3))
