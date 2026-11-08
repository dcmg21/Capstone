"""
STEP 5 at a 500-case floor. Same test as step05_predict.py, only MIN_CASES differs.
Run this to answer "what if the floor were 500?" without touching the paper's numbers.

Two questions, answered one after the other in the same run:
    viable    Will the brand still be healthy (stable or growing) next year?   Kristin's 1.
    growing   Will the brand be growing next year?                              The invest question.

How the test works:
    For each brand, take what we knew at the end of one year and the label at the end of the next.
    Learn from 2022->2023 and 2023->2024.  Test on 2024->2025, which the models never see.

What the models are given (all as of the year we know):
    sales vs best, stores vs best, store trend      the three numbers behind the label
    store coverage now, brand size, brand age       new in this version
    sales growth vs the year before                 Dr. Sadler's whiteboard number
    momentum (quarters in a row near its best)
    category growth, brand vs its category          category context (Nov 2026, Eurpac's ask)
    current label, category, price tier

Two models, two baselines:
    stays the same        next year's 1/0 = this year's 1/0.  Hard to beat.
    growth only           last year's sales growth alone (the whiteboard)
    logistic regression   simple, explainable
    gradient boosting     handles "small brands behave differently from big ones" on its own

How we score (on the test year):
    hit rate top 100   of the 100 brands a model is most sure about, how many were actually 1?
    balanced accuracy  Kristin's metric.  AUC: overall ranking quality.

What the models lean on:
    logistic regression   its coefficients (positive = pushes toward 1). Easy to read.
    gradient boosting     has no coefficients, so we shuffle one input at a time on the test year
                          and see how much the ranking gets worse. Big drop = the model relied on it.
    Shown side by side so you can see whether the two models agree on what matters.

Run the whole file. You get `results` (both questions), `top` (the ranked test lists), `importance`.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from step01_load_data import load_sales  # noqa: E402
from step02_label import COLUMNS, TIERS, label_all  # noqa: E402

TEST_YEAR = 2025      # predict this year-end from the one before
MIN_CASES = 500       # the floor Jacob mentioned. The paper's numbers are at 250 (step05_predict.py).
                      # Without it, 19-case brands flood the top of the list. Ask Eurpac for their number.
TOP = [100, 500]
PER_CATEGORY = 10

INPUTS = ["sales_vs_best", "stores_vs_best", "store_trend",   # the three numbers behind the label
          "store_coverage", "brand_size", "brand_age",       # %ACV now, cases last year (logged), years in the data
          "sales_growth",                                    # cases this year / last year
          "quarters_at_best",                                # momentum: quarters in a row near its best
          "category_growth", "vs_category"]                  # category context: how the category grew, and the brand vs it
# Tried and set aside (near-zero importance): "price", "promo_share". Step 2 still computes them.


def prepare_inputs(labels, min_cases=MIN_CASES):
    """Clean the label table into model inputs. Keeps only brands over the size floor."""
    lab = labels.copy()
    lab["growing"] = (lab["label"] == "growing").astype(int)
    lab["brand_size"] = np.log1p(lab["cases_last_year"])
    lab["brand_age"] = lab["weeks_of_history"] / 52
    lab["store_trend"] = lab["store_trend"].fillna(1.0).clip(upper=5)      # no prior year = flat; cap wild ratios
    lab["sales_growth"] = lab["sales_growth"].fillna(1.0).clip(upper=5)
    lab["category_growth"] = lab["category_growth"].fillna(1.0)
    lab["vs_category"] = lab["vs_category"].fillna(1.0).clip(upper=5)     # no prior year = moved with the category
    lab[["sales_vs_best", "stores_vs_best"]] = lab[["sales_vs_best", "stores_vs_best"]].fillna(0)
    lab["price"] = np.log1p(lab["price"].fillna(lab["price"].median()))   # logged: $10 vs $20 matters more than $200 vs $210
    lab["promo_share"] = lab["promo_share"].fillna(0).clip(0, 1)
    lab["price_tier"] = lab["price_tier"].astype(str)
    lab["category"] = lab["category"].astype(str)
    return lab[lab["cases_last_year"] >= min_cases]


def build_rows(labels):
    """One row per brand per year: inputs as of year t, the label at the end of year t+1."""
    lab = prepare_inputs(labels)
    nxt = labels[["brand", "as_of", "viable", "label"]].assign(growing=lambda d: (d["label"] == "growing").astype(int))
    nxt = nxt[["brand", "as_of", "viable", "growing"]].rename(
        columns={"as_of": "year_known", "viable": "viable_next", "growing": "growing_next"})
    nxt["year_known"] -= 1
    return lab.merge(nxt, left_on=["brand", "as_of"], right_on=["brand", "year_known"]).drop(columns="year_known")


def design(rows, columns=None):
    """Numbers in, plus 0/1 columns for the label, category and price tier.
    One value of each is left out as the reference (discontinued, and the first category and
    price tier alphabetically), so every coefficient reads "compared with the reference"."""
    X = rows[INPUTS].copy()
    for t in TIERS[1:]:                                   # discontinued is the reference
        X["tier_" + t] = (rows["label"] == t).astype(int)
    dummies = pd.get_dummies(rows[["category", "price_tier"]], dtype=int, drop_first=True)
    X = pd.concat([X, dummies], axis=1)
    return X if columns is None else X.reindex(columns=columns, fill_value=0)


def score(name, y, p, pred):
    out = {"model": name, "balanced_accuracy": balanced_accuracy_score(y, pred), "auc": roc_auc_score(y, p)}
    order = np.argsort(-p)
    for k in TOP:
        out[f"hit_rate_top{k}"] = y.to_numpy()[order[:k]].mean()
    return out


def run(target, train, test, Xtr, Xte):
    """Baselines and models for one target. Returns the results table and each model's probabilities."""
    ytr, yte = train[target + "_next"], test[target + "_next"]
    rows, probs = [], {}

    # baseline 1: nothing changes (tiny tiebreak so the ranking is not random inside the 1s)
    same = test[target].to_numpy().astype(float)
    probs["stays the same"] = same + 1e-6 * test["stores_vs_best"].to_numpy()
    rows.append(score("stays the same", yte, probs["stays the same"], same))

    # baseline 2: last year's sales growth only
    lr1 = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced"))
    lr1.fit(train[["sales_growth"]], ytr)
    probs["growth only"] = lr1.predict_proba(test[["sales_growth"]])[:, 1]
    rows.append(score("growth only", yte, probs["growth only"], probs["growth only"] >= 0.5))

    # model 1: logistic regression
    lr = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=3000))
    lr.fit(Xtr, ytr)
    probs["logistic regression"] = lr.predict_proba(Xte)[:, 1]
    rows.append(score("logistic regression", yte, probs["logistic regression"], probs["logistic regression"] >= 0.5))

    # model 2: gradient boosting
    gb = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=300, class_weight="balanced", random_state=0)
    gb.fit(Xtr, ytr)
    probs["gradient boosting"] = gb.predict_proba(Xte)[:, 1]
    rows.append(score("gradient boosting", yte, probs["gradient boosting"], probs["gradient boosting"] >= 0.5))

    # what each model leans on
    imp = permutation_importance(gb, Xte, yte, scoring="roc_auc", n_repeats=5, random_state=0)
    importance = pd.DataFrame({"logistic_coefficient": lr[-1].coef_[0],
                               "boosting_importance": imp.importances_mean}, index=Xtr.columns).round(3)
    importance = importance.reindex(importance["boosting_importance"].abs().sort_values(ascending=False).index)
    return pd.DataFrame(rows).set_index("model").round(3), probs, importance


if __name__ == "__main__":
    sales = load_sales(columns=COLUMNS)
    rows = build_rows(label_all(sales))
    train, test = rows[rows["as_of"] < TEST_YEAR - 1], rows[rows["as_of"] == TEST_YEAR - 1]
    Xtr = design(train)
    Xte = design(test, Xtr.columns)
    print(f"Brands with {MIN_CASES}+ cases in the year we know: {len(train):,} training rows "
          f"(2022->2023, 2023->2024), {len(test):,} test rows (2024->2025)\n")

    results, top, importance = {}, {}, {}
    for target in ["viable", "growing"]:
        res, probs, importance[target] = run(target, train, test, Xtr, Xte)
        results[target] = res
        best = res["hit_rate_top100"].idxmax()
        y = test[target + "_next"]

        print("=" * 78)
        print(f"QUESTION: will the brand be {target.upper()} next year?   "
              f"(random picking would hit {y.mean():.1%})")
        print("=" * 78)
        print(res.to_string())
        print(f"\nBest at the top of the list: {best}")

        ranked = test.assign(p_next_year=probs[best].round(3)).sort_values("p_next_year", ascending=False)
        top[target] = ranked[["brand", "category", "label", "cases_last_year", "p_next_year", target + "_next"]]
        print(f"\nTop 15 picks by {best} (last column = what actually happened):")
        print(top[target].head(15).to_string(index=False))

        by_cat = ranked.groupby("category").head(PER_CATEGORY).groupby("category")[target + "_next"].agg(picks="size", were_1="sum")
        by_cat["hit_rate"] = (by_cat["were_1"] / by_cat["picks"]).round(2)
        print(f"\nTop {PER_CATEGORY} per category by {best}: how many were actually 1 a year later?")
        print(by_cat.sort_values("hit_rate", ascending=False).to_string())

        print("\nWhat the models lean on. logistic_coefficient: positive pushes toward 1."
              " boosting_importance: how much the ranking worsens when this input is shuffled.")
        print(importance[target].head(12).to_string())
        print()
