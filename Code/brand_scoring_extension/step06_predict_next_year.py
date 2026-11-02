"""
STEP 6: Predict next year for every brand, on the newest data.

Step 5 pretended it was the end of 2024 and checked its predictions against 2025. That proved
the models. This step stands at the end of the newest year and predicts the year nobody has
seen yet. Same models, same inputs, real predictions.
    1. Label every brand at every year-end (step 2).
    2. Train on every year-to-year step we have (no hold-out now; the test is done).
    3. Score every brand as of the newest year-end: chance of being viable next year
       (logistic regression) and chance of growing (gradient boosting).

The chances are calibrated: both models are trained to treat yes and no as equally common
(class_weight="balanced"), which is right for ranking but stretches the raw numbers, growing's
more than viable's because growing is rarer. A calibration step maps each model's score back to
how often brands with that score really did turn out yes in the training years. So "0.65" means
about 65 in 100. The ordering of brands does not change, so step 5's hit rates still apply.
Growing is part of viable, so viable should come out the larger chance; the two models are
separate, so nothing forces it. The main block prints how often they disagree.

Run the whole file. You get:
    predictions        every brand: label today, reason, both chances, rank overall, rank in category
    top_per_category   the TOP_PER_CATEGORY highest growing chances in each category
Nothing is written to disk. Open `predictions` in the Data Explorer.
"""

import sys
from pathlib import Path

from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from step01_load_data import load_sales  # noqa: E402
from step02_label import COLUMNS, label_all  # noqa: E402
from step05_predict import MIN_CASES, build_rows, design, prepare_inputs  # noqa: E402

TOP_PER_CATEGORY = 10


def calibrated(model, X, y):
    """Fit the model on all rows, then learn how its scores map to real yes rates (5-fold).
    'sigmoid' keeps the ordering of brands exactly as the raw model had it."""
    return CalibratedClassifierCV(model, method="sigmoid", cv=5, ensemble=False).fit(X, y)


def fit_models(rows):
    """Train on every year-to-year step available. Returns the two fitted models and the column order."""
    X = design(rows)
    viable_model = calibrated(
        make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=3000)),
        X, rows["viable_next"])
    growing_model = calibrated(
        HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=300,
                                       class_weight="balanced", random_state=0),
        X, rows["growing_next"])
    return viable_model, growing_model, X.columns


def score_latest(labels, viable_model, growing_model, columns, min_cases=MIN_CASES):
    """Score every brand as of the newest year-end (brands under min_cases are listed but not scored)."""
    latest_year = labels["as_of"].max()
    latest = labels[labels["as_of"] == latest_year].copy()
    big = prepare_inputs(latest, min_cases)
    X = design(big, columns)
    big["chance_viable_next_year"] = viable_model.predict_proba(X)[:, 1].round(3)
    big["chance_growing_next_year"] = growing_model.predict_proba(X)[:, 1].round(3)

    out = latest.merge(big[["brand", "chance_viable_next_year", "chance_growing_next_year"]], on="brand", how="left")
    out["rank_overall"] = out["chance_growing_next_year"].rank(ascending=False, method="min").astype("Int64")
    out["rank_in_category"] = (out.groupby("category", observed=True)["chance_growing_next_year"]
                                  .rank(ascending=False, method="min").astype("Int64"))
    out["years_of_data"] = (out["weeks_of_history"] / 52).round(1)
    cols = ["brand", "family", "category", "price_tier", "cases_last_year", "years_of_data", "label", "viable", "reason",
            "chance_viable_next_year", "chance_growing_next_year", "rank_overall", "rank_in_category"]
    return out[cols].sort_values("rank_overall"), latest_year


if __name__ == "__main__":
    sales = load_sales(columns=COLUMNS)
    labels = label_all(sales)
    rows = build_rows(labels)
    viable_model, growing_model, columns = fit_models(rows)
    print(f"Trained on {len(rows):,} brand-years ({', '.join(f'{y}->{y+1}' for y in sorted(rows['as_of'].unique()))})")

    predictions, year = score_latest(labels, viable_model, growing_model, columns)
    n_scored = predictions["chance_growing_next_year"].notna().sum()
    print(f"Scored {n_scored:,} of {len(predictions):,} brands as of the end of {year}, looking at {year + 1} "
          f"(the rest sold under {MIN_CASES} cases and are listed without scores)")
    scored = predictions.dropna(subset=["chance_growing_next_year"])
    flipped = (scored["chance_growing_next_year"] > scored["chance_viable_next_year"]).sum()
    print(f"Check: growing chance above viable chance for {flipped:,} of {len(scored):,} brands "
          f"(growing is part of viable, so this should be near zero)")

    top_per_category = (predictions.dropna(subset=["chance_growing_next_year"])
                                   .sort_values(["category", "rank_in_category"])
                                   .groupby("category", observed=True).head(TOP_PER_CATEGORY))

    print(f"\nTop 10 overall by chance of growing in {year + 1}:")
    print(predictions.head(10)[["brand", "category", "label", "cases_last_year", "chance_viable_next_year",
                                "chance_growing_next_year"]].to_string(index=False))
    del sales, rows, viable_model, growing_model, columns
