"""
Build the four files the app reads. Run this once, and again whenever new NIQ data arrives.

    data/predictions.parquet   one row per brand as of the newest year-end: label, reason, both chances
    data/labels.parquet        one row per brand per year-end (the trajectory view)
    data/weekly.parquet        cases and store coverage per brand per week (the charts)
    data/suppliers.parquet     one row per brand: its supplier (NIQ's BRAND OWNER)

Models are trained on brands with TRAIN_FLOOR+ cases (what step 5 tested). Scores are then
produced for every brand down to SCORE_FLOOR cases, so the app's size slider has room to move.

Run from the Code folder:   python app/build_app_data.py
"""

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "brand_scoring_extension"))

from step01_load_data import load_sales  # noqa: E402
from step02_label import BRAND, COLUMNS, label_all  # noqa: E402
from step05_predict import MIN_CASES, build_rows  # noqa: E402
from step06_predict_next_year import fit_models, score_latest  # noqa: E402

TRAIN_FLOOR = MIN_CASES   # 250: the floor the models were validated at
SCORE_FLOOR = 12          # score everything down to one case a month; the app slider decides what to show
GAP_WEEKS = 26            # half a year effectively unsold (under GAP_CASES a week), after first appearing, marks it "comes and goes"
GAP_CASES = 1.0           # a bottle here and there in one store still counts as gone
DATA = HERE / "data"


def full_week_grid(weekly):
    """One row per brand per week from its first week to the end of the data, with 0 cases and 0 coverage
    in weeks it did not sell. This is the grid step 2 labels from (weekly_tables), so the 13-week average
    on the brand chart is the same one the labels were read from."""
    last = int(weekly["week"].max())
    first = weekly.groupby("brand")["week"].min()
    n = (last - first + 1).to_numpy()
    offset = np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)
    grid = pd.DataFrame({"brand": np.repeat(first.index.to_numpy(), n),
                         "week": (np.repeat(first.to_numpy(), n) + offset).astype(weekly["week"].dtype)})
    dates = weekly.drop_duplicates("week").set_index("week")["period_date"]
    out = grid.merge(weekly.drop(columns="period_date"), on=["brand", "week"], how="left")
    out["period_date"] = out["week"].map(dates)
    out[["cases", "store_coverage"]] = out[["cases", "store_coverage"]].fillna(0)
    return out[["brand", "week", "period_date", "cases", "store_coverage"]]


def comes_and_goes(weekly, gap=GAP_WEEKS, floor=GAP_CASES):
    """True for brands with a run of `gap`+ weeks selling under `floor` cases a week, somewhere after they first
    sold properly: seasonal items, limited runs, relaunches. Their 'vs best' and 'vs a year ago' numbers measure a calendar."""
    piv = weekly.pivot_table(index="brand", columns="week", values="cases").reindex(columns=range(1, weekly["week"].max() + 1))
    sold = (piv.fillna(0) >= floor).to_numpy()
    seen = np.cumsum(sold, axis=1) > 0                      # True from the first real week of sales onward
    quiet = seen & ~sold                                    # a week after launch with next to nothing sold
    longest = np.zeros(len(piv), dtype=int)
    run = np.zeros(len(piv), dtype=int)
    for j in range(quiet.shape[1]):
        run = np.where(quiet[:, j], run + 1, 0)
        longest = np.maximum(longest, run)
    return pd.Series(longest >= gap, index=piv.index, name="comes_and_goes")

if __name__ == "__main__":
    t0 = time.time()
    DATA.mkdir(exist_ok=True)

    sales = load_sales(columns=COLUMNS + ["period_date", "BRAND OWNER"])
    labels = label_all(sales)

    rows = build_rows(labels)                                     # training rows, TRAIN_FLOOR applied inside
    viable_model, growing_model, columns = fit_models(rows)
    predictions, year = score_latest(labels, viable_model, growing_model, columns, min_cases=SCORE_FLOOR)
    predictions["as_of"] = year
    # The two models are fit and calibrated separately, so a few brands come out with growing > viable.
    # Every growing brand is viable, so viable can never be the smaller chance: lift it to growing.
    flipped = (predictions["chance_growing_next_year"] > predictions["chance_viable_next_year"]).sum()
    predictions["chance_viable_next_year"] = predictions[["chance_viable_next_year",
                                                          "chance_growing_next_year"]].max(axis=1, skipna=False)

    weekly = (sales.groupby([BRAND, "week", "period_date"], observed=True)
                   .agg(cases=("Case", "sum"), store_coverage=("%ACV", "max")).reset_index()
                   .rename(columns={BRAND: "brand"}))
    weekly["brand"] = weekly["brand"].astype(str)
    weekly["cases"] = weekly["cases"].clip(lower=0)
    flag = comes_and_goes(weekly)                                 # on NIQ's reported weeks, before the zero-filled grid
    predictions["comes_and_goes"] = predictions["brand"].map(flag).fillna(False).astype(bool)
    weekly = full_week_grid(weekly)

    # supplier = NIQ's BRAND OWNER; when an extension has more than one, the one with the most cases
    owners = (sales.groupby([BRAND, "BRAND OWNER"], observed=True)["Case"].sum().reset_index()
                   .sort_values("Case", ascending=False).drop_duplicates(BRAND))
    suppliers = pd.DataFrame({"brand": owners[BRAND].astype(str), "supplier": owners["BRAND OWNER"].astype(str)})

    predictions.to_parquet(DATA / "predictions.parquet", index=False)
    labels.to_parquet(DATA / "labels.parquet", index=False)
    weekly.to_parquet(DATA / "weekly.parquet", index=False)
    suppliers.to_parquet(DATA / "suppliers.parquet", index=False)

    scored = predictions["chance_growing_next_year"].notna().sum()
    print(f"predictions: {len(predictions):,} brands as of end of {year}, {scored:,} scored (>= {SCORE_FLOOR} cases)")
    print(f"             {flipped:,} had chance growing > chance viable; viable lifted to match")
    print(f"labels:      {len(labels):,} brand-years")
    print(f"comes and goes: {int(predictions['comes_and_goes'].sum()):,} brands with a {GAP_WEEKS}+ week stretch of no sales")
    print(f"weekly:      {len(weekly):,} brand-weeks")
    print(f"suppliers:   {suppliers['supplier'].nunique():,} suppliers")
    print(f"Wrote 4 files to {DATA} in {time.time() - t0:.0f}s")
