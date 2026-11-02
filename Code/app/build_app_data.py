"""
Build the three files the app reads. Run this once, and again whenever new NIQ data arrives.

    data/predictions.parquet   one row per brand as of the newest year-end: label, reason, both chances
    data/labels.parquet        one row per brand per year-end (the trajectory view)
    data/weekly.parquet        cases and store coverage per brand per week (the charts)

Models are trained on brands with TRAIN_FLOOR+ cases (what step 5 tested). Scores are then
produced for every brand down to SCORE_FLOOR cases, so the app's size slider has room to move.

Run from the Code folder:   python app/build_app_data.py
"""

import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "brand_scoring_extension"))

from step01_load_data import load_sales  # noqa: E402
from step02_label import BRAND, COLUMNS, label_all  # noqa: E402
from step05_predict import MIN_CASES, build_rows  # noqa: E402
from step06_predict_next_year import fit_models, score_latest  # noqa: E402

TRAIN_FLOOR = MIN_CASES   # 250: the floor the models were validated at
SCORE_FLOOR = 12          # score everything down to one case a month; the app slider decides what to show
DATA = HERE / "data"

if __name__ == "__main__":
    t0 = time.time()
    DATA.mkdir(exist_ok=True)

    sales = load_sales(columns=COLUMNS + ["period_date"])
    labels = label_all(sales)

    rows = build_rows(labels)                                     # training rows, TRAIN_FLOOR applied inside
    viable_model, growing_model, columns = fit_models(rows)
    predictions, year = score_latest(labels, viable_model, growing_model, columns, min_cases=SCORE_FLOOR)
    predictions["as_of"] = year

    weekly = (sales.groupby([BRAND, "week", "period_date"], observed=True)
                   .agg(cases=("Case", "sum"), store_coverage=("%ACV", "max")).reset_index()
                   .rename(columns={BRAND: "brand"}))
    weekly["brand"] = weekly["brand"].astype(str)
    weekly["cases"] = weekly["cases"].clip(lower=0)

    predictions.to_parquet(DATA / "predictions.parquet", index=False)
    labels.to_parquet(DATA / "labels.parquet", index=False)
    weekly.to_parquet(DATA / "weekly.parquet", index=False)

    scored = predictions["chance_growing_next_year"].notna().sum()
    print(f"predictions: {len(predictions):,} brands as of end of {year}, {scored:,} scored (>= {SCORE_FLOOR} cases)")
    print(f"labels:      {len(labels):,} brand-years")
    print(f"weekly:      {len(weekly):,} brand-weeks")
    print(f"Wrote 3 files to {DATA} in {time.time() - t0:.0f}s")
