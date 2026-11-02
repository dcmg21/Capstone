"""
auto_label.py
=============
Automates the truth-set hand labeling from truth_set_labeling.Rmd.

The hand labeler looked at each brand's Cases and %ACV plots (13-week moving
average, "focus on a consistent signal over the past 2 years") and picked one of
    discontinued / decline / stable / growing.
This script turns what the eye was doing into three numbers per brand and four
if/else rules on those numbers.

The three numbers (all ratios, so they work for big and small brands alike and
do not depend on whether %ACV is stored as 0-1 or 0-100):

    cases_vs_peak  last 13 weeks' mean cases  /  the brand's highest 13-week moving average
    acv_vs_peak    same thing for %ACV                ("how far from its best is it now?")
    acv_yoy        mean %ACV over the last 52 weeks  /  mean %ACV over the 52 weeks before
                                                       ("is distribution trending up or down?")

The rules, checked in this order (first match wins):

    1. discontinued  cases_vs_peak < 10%  AND  acv_vs_peak < 10%
                     (sales and distribution have both all but vanished)
    2. growing       cases_vs_peak >= 80% AND  acv_yoy >= 1.03
                     (selling near its best right now and distribution still rising)
    3. decline       acv_yoy < 0.90       OR   acv_vs_peak < 40%
                     (distribution down 10%+ on the year, or well off its peak)
    4. stable        everything else

Vodka result: 91% agreement with the 112 hand labels (Cohen's kappa 0.88).
Re-tuning the thresholds on 4/5 of the labels and scoring the held-out 1/5
gives about 90% (--tune), so the thresholds are not just memorizing the truth set.
Most misses are borderline calls (e.g. decline vs discontinued for a brand
selling 2% of its peak).

A second, separate label from the Sadler 09/27 meeting is also added:
    invest = cases grew >= INVEST_GROWTH from Year 2 to Year 3,
    for brands with sales in all three of the last 52-week years.
growth_y1_y2 is kept as the explanatory variable for the planned logistic regression.

Needs pandas, numpy, pyarrow, scikit-learn (scoring/tuning), matplotlib (--plots);
all are in the Capstone/.venv.

Usage (from the labeling_automation folder):
    python auto_label.py                                   # vodka, scored against the truth set
    python auto_label.py --category GIN                    # any ALC CATEGORY value
    python auto_label.py --subcategory "WHISKEY AMERICAN"  # or an ALC SUBCATEGORY value
    python auto_label.py --category GIN --all-extensions   # include multi-extension families
    python auto_label.py --category GIN --plots 5          # PDF of 5 random brands per label to spot-check
    python auto_label.py --tune                            # grid-search thresholds against the truth set

Inputs:  capstone_code/data/data/sales_dataset_spirits_weeks/ (from 01_data_preparation.R)
         vodka_single_ext_truth_set.csv (optional, only used for scoring)
Outputs: outputs/<category>_auto_labels.csv  (brand names inside: NDA, keep local)
         outputs/<category>_spot_check.pdf   (only with --plots)
"""

import argparse
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

# =============================================================================
# CONFIG
# =============================================================================
HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parents[1] / "capstone_code" / "data" / "sales_dataset_spirits_weeks"
TRUTH_CSV = HERE.parent / "k_eurpac" / "outputs" / "vodka_single_ext_truth_set.csv"
OUT_DIR = HERE / "outputs"

MIN_WEEKS = 52     # same history filter as the Rmd
MA_WEEKS = 13      # moving-average window used in the Rmd plots
YEAR = 52          # one "year" = 52 weeks (same as YearBucket)

# Labeling thresholds (see the module docstring for what each one means)
THRESHOLDS = dict(
    dead=0.10,          # discontinued: cases AND %ACV both below this share of their peak
    near_peak=0.80,     # growing: recent cases at least this share of peak ...
    grow_yoy=1.03,      # ... and %ACV year-over-year ratio at least this
    decline_yoy=0.90,   # decline: %ACV year-over-year ratio below this ...
    decline_peak=0.40,  # ... or recent %ACV below this share of its peak
)

INVEST_GROWTH = 0.25   # Sadler notes: "e.g. 25%" (50% was also floated). A knob to adjust.

LABELS = ["discontinued", "decline", "stable", "growing"]
KEYS = ["ALC BRAND FAMILY", "ALC BRAND EXTENSION"]   # one brand = one (family, extension) pair, as in the Rmd


# =============================================================================
# STEP 1: Load weekly data for the target category
# =============================================================================
def load_weekly(category=None, subcategory=None, single_ext_only=True):
    """One row per brand extension per week: summed Cases, max %ACV across UPCs.
    (Same aggregation as the Rmd: a brand has distribution if any of its UPCs does.)"""
    cols = ["ALC BRAND FAMILY", "ALC BRAND EXTENSION", "ALC CATEGORY", "ALC SUBCATEGORY",
            "week", "Case", "%ACV"]
    df = pd.read_parquet(DATA_DIR, columns=cols)

    # Which brands have any rows in the target category/subcategory?
    in_target = df["ALC CATEGORY"].eq(category) if category else df["ALC SUBCATEGORY"].eq(subcategory)
    brands = df.loc[in_target, KEYS].drop_duplicates()

    # Single-extension families: family view == extension view, so labels are unambiguous.
    # Extensions are counted across ALL categories, as in the Rmd.
    if single_ext_only:
        n_ext = df.groupby("ALC BRAND FAMILY")["ALC BRAND EXTENSION"].nunique()
        brands = brands[brands["ALC BRAND FAMILY"].isin(n_ext[n_ext == 1].index)]

    df = df.merge(brands, on=KEYS)   # keep all of those brands' rows, as in the Rmd
    weekly = (df.groupby(KEYS + ["week"])
                .agg(cases=("Case", "sum"), acv=("%ACV", "max"))
                .reset_index())
    weekly["cases"] = weekly["cases"].clip(lower=0)   # negative returns count as zero
    weekly["acv"] = weekly["acv"].fillna(0)           # blank %ACV = 0, as in the Rmd plots
    return weekly


# =============================================================================
# STEP 2: Turn each brand's trajectory into a few numbers
# =============================================================================
def to_wide(weekly, value):
    """Brand x week table (one row per brand, one column per week), like reading the plot
    left to right. Weeks before a brand's first appearance are NaN (not yet launched);
    weeks after launch with no row are 0 (nothing sold)."""
    end = weekly["week"].max()
    wide = weekly.pivot(index=KEYS, columns="week", values=value)
    wide = wide.reindex(columns=range(1, end + 1))
    launched = wide.notna().cumsum(axis=1) > 0
    return wide.fillna(0).where(launched)


def compute_features(weekly):
    cases, acv = to_wide(weekly, "cases"), to_wide(weekly, "acv")

    def recent_vs_peak(wide):
        peak = wide.T.rolling(MA_WEEKS, min_periods=1).mean().max()   # highest 13-wk average
        return wide.iloc[:, -MA_WEEKS:].mean(axis=1) / peak

    def yoy(wide):
        last = wide.iloc[:, -YEAR:].mean(axis=1)
        prev = wide.iloc[:, -2 * YEAR:-YEAR].mean(axis=1)   # NaN-skipping, so partial years are OK
        return last / prev.replace(0, np.nan)

    feats = pd.DataFrame({
        "n_weeks": weekly.groupby(KEYS)["week"].nunique(),
        "first_week": weekly.groupby(KEYS)["week"].min(),
        "mean_cases": cases.mean(axis=1),
        "mean_acv": acv.mean(axis=1),
        "cases_vs_peak": recent_vs_peak(cases),
        "acv_vs_peak": recent_vs_peak(acv),
        "acv_yoy": yoy(acv),
        "cases_yoy": yoy(cases),   # not used by the rules; handy context when reviewing
    })

    # Sadler invest label: three consecutive 52-week years ending at the last week of data
    y1, y2, y3 = (cases.iloc[:, -3 * YEAR:-2 * YEAR].sum(axis=1, min_count=YEAR),
                  cases.iloc[:, -2 * YEAR:-YEAR].sum(axis=1),
                  cases.iloc[:, -YEAR:].sum(axis=1))
    complete = (y1 > 0) & (y2 > 0) & (y3 > 0)   # min_count=YEAR: launched before Year 1 started
    feats["cases_y1"], feats["cases_y2"], feats["cases_y3"] = y1, y2, y3
    feats["growth_y1_y2"] = (y2 / y1 - 1).where(complete)
    feats["growth_y2_y3"] = (y3 / y2 - 1).where(complete)
    feats["invest"] = np.where(complete, np.where(feats["growth_y2_y3"] >= INVEST_GROWTH,
                                                  "invest", "not_invest"), pd.NA)
    return feats.reset_index()


# =============================================================================
# STEP 3: Apply the rules
# =============================================================================
def apply_rules(f, dead, near_peak, grow_yoy, decline_yoy, decline_peak):
    """Returns (label, reason) arrays. First matching rule wins."""
    yoy = f["acv_yoy"].fillna(1.0)   # no prior-year data -> treat as flat
    rules = [
        ("discontinued", (f["cases_vs_peak"] < dead) & (f["acv_vs_peak"] < dead)),
        ("growing",      (f["cases_vs_peak"] >= near_peak) & (yoy >= grow_yoy)),
        ("decline",      (yoy < decline_yoy) | (f["acv_vs_peak"] < decline_peak)),
    ]
    label = np.select([cond for _, cond in rules], [name for name, _ in rules], "stable")

    pct = lambda s: (100 * s).round(0).astype("Int64").astype(str) + "%"
    reason = ("cases " + pct(f["cases_vs_peak"]) + " of peak, %ACV " + pct(f["acv_vs_peak"])
              + " of peak, %ACV YoY x" + f["acv_yoy"].round(2).astype(str))
    return label, reason


# =============================================================================
# STEP 4: Compare to the hand labels
# =============================================================================
def load_truth():
    t = pd.read_csv(TRUTH_CSV)[KEYS + ["truth_label"]]
    return t[t["truth_label"].isin(LABELS)]


def score(df):
    """Agreement, Cohen's kappa, confusion matrix, and the disagreements to look at."""
    from sklearn.metrics import cohen_kappa_score
    lab = df[df["truth_label"].isin(LABELS)]
    agree = (lab["auto_label"] == lab["truth_label"]).mean()
    print(f"\nScored on {len(lab)} hand-labeled brands")
    print(f"  agreement: {agree:.1%}   Cohen's kappa: {cohen_kappa_score(lab['truth_label'], lab['auto_label']):.3f}")
    print(pd.crosstab(lab["truth_label"], lab["auto_label"], rownames=["hand"], colnames=["auto"], margins=True)
            .reindex(index=LABELS + ["All"], columns=LABELS + ["All"], fill_value=0))
    miss = lab[lab["auto_label"] != lab["truth_label"]]
    if len(miss):
        print("\nDisagreements:")
        print(miss[["ALC BRAND EXTENSION", "truth_label", "auto_label", "reason"]].to_string(index=False))


def tune(df, n_splits=5, n_repeats=10, seed=0):
    """Grid-search the thresholds against the hand labels. Reports in-sample best and a
    cross-validated agreement where thresholds are picked on training folds only."""
    from sklearn.model_selection import RepeatedStratifiedKFold
    grid = dict(dead=[0.05, 0.10, 0.15, 0.20], near_peak=[0.7, 0.8, 0.9],
                grow_yoy=[1.0, 1.03, 1.05, 1.1], decline_yoy=[0.85, 0.90, 0.95],
                decline_peak=[0.3, 0.4, 0.5])
    combos = [dict(zip(grid, vals)) for vals in itertools.product(*grid.values())]
    lab = df[df["truth_label"].isin(LABELS)].reset_index(drop=True)
    acc = lambda d, p: (apply_rules(d, **p)[0] == d["truth_label"]).mean()
    best = lambda d: max(combos, key=lambda p: acc(d, p))

    p = best(lab)
    print(f"\nIn-sample best thresholds ({acc(lab, p):.1%}): {p}")
    print(f"Current THRESHOLDS ({acc(lab, THRESHOLDS):.1%}): {THRESHOLDS}")
    scores = []
    for tr, te in RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=seed) \
            .split(lab, lab["truth_label"]):
        scores.append(acc(lab.iloc[te], best(lab.iloc[tr])))
    print(f"Cross-validated agreement ({n_splits}-fold x {n_repeats}): "
          f"{np.mean(scores):.1%} (sd {np.std(scores):.1%})")


# =============================================================================
# STEP 5 (optional): Spot-check PDF, same panels as the Rmd
# =============================================================================
def spot_check_pdf(df, weekly, n_per_label, path, seed=0):
    """A few random brands per auto label: Cases (blue) and %ACV (green), thin = weekly,
    thick = 13-week moving average. Flip through it to sanity-check a new category."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    picks = df.sample(frac=1, random_state=seed).groupby("auto_label").head(n_per_label) \
              .sort_values("auto_label")
    cases, acv = to_wide(weekly, "cases"), to_wide(weekly, "acv")
    with PdfPages(path) as pdf:
        for start in range(0, len(picks), 3):
            fig, axes = plt.subplots(3, 2, figsize=(14, 12), squeeze=False)
            for row, (_, b) in zip(axes, picks.iloc[start:start + 3].iterrows()):
                ext = b["ALC BRAND EXTENSION"]
                for ax, wide, color, name in [(row[0], cases, "steelblue", "Cases"),
                                              (row[1], acv, "darkgreen", "%ACV")]:
                    s = wide.loc[(b["ALC BRAND FAMILY"], ext)]
                    ax.plot(s.index, s, color=color, alpha=0.4, lw=0.6)
                    ax.plot(s.index, s.rolling(MA_WEEKS).mean(), color=color, lw=1.6)
                    ax.set_ylabel(name, color=color)
                    ax.set_ylim(bottom=0)
                row[0].set_title(f"{ext}  ->  {b['auto_label'].upper()}"
                                 + (f"  (hand: {b['truth_label']})" if pd.notna(b.get("truth_label")) else ""),
                                 loc="left", fontsize=10, fontweight="bold")
                row[1].set_title(b["reason"], loc="left", fontsize=9)
            for ax in axes[len(picks.iloc[start:start + 3]):].ravel():
                ax.axis("off")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
    print("Wrote", path)


# =============================================================================
# MAIN
# =============================================================================
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    target = ap.add_mutually_exclusive_group()
    target.add_argument("--category", help="ALC CATEGORY value (default VODKA)")
    target.add_argument("--subcategory", help="ALC SUBCATEGORY value")
    ap.add_argument("--all-extensions", action="store_true",
                    help="label every brand extension, not just single-extension families")
    ap.add_argument("--plots", type=int, default=0, metavar="N", help="spot-check PDF with N brands per label")
    ap.add_argument("--tune", action="store_true", help="grid-search thresholds against the truth set")
    args = ap.parse_args()
    category = args.category or (None if args.subcategory else "VODKA")
    name = (category or args.subcategory).lower().replace(" ", "_")

    print(f"Loading weekly data for {category or args.subcategory} ...")
    weekly = load_weekly(category, args.subcategory, single_ext_only=not args.all_extensions)
    feats = compute_features(weekly)
    feats = feats[feats["n_weeks"] >= MIN_WEEKS].copy()
    feats["auto_label"], feats["reason"] = apply_rules(feats, **THRESHOLDS)

    # Attach hand labels where we have them (only vodka for now)
    if TRUTH_CSV.exists():
        feats = feats.merge(load_truth(), on=KEYS, how="left")
    else:
        print(f"Truth set not found at {TRUTH_CSV}; skipping scoring")
        feats["truth_label"] = pd.NA

    print(f"{len(feats)} brands with >= {MIN_WEEKS} weeks of history")
    print("Auto label counts:\n" + feats["auto_label"].value_counts().reindex(LABELS, fill_value=0).to_string())
    print("Invest label counts (Sadler, Y2->Y3 growth >= "
          f"{INVEST_GROWTH:.0%}):\n" + feats["invest"].value_counts(dropna=False).to_string())

    if feats["truth_label"].notna().any():
        score(feats)
        if args.tune:
            tune(feats)

    OUT_DIR.mkdir(exist_ok=True)
    cols = ["ALC BRAND FAMILY", "ALC BRAND EXTENSION", "auto_label", "truth_label", "reason",
            "n_weeks", "first_week", "mean_cases", "mean_acv",
            "cases_vs_peak", "acv_vs_peak", "acv_yoy", "cases_yoy",
            "cases_y1", "cases_y2", "cases_y3", "growth_y1_y2", "growth_y2_y3", "invest"]
    out_csv = OUT_DIR / f"{name}_auto_labels.csv"
    feats[cols].sort_values(["auto_label", "ALC BRAND EXTENSION"]).to_csv(out_csv, index=False)
    print("\nWrote", out_csv)

    if args.plots:
        spot_check_pdf(feats, weekly, args.plots, OUT_DIR / f"{name}_spot_check.pdf")


if __name__ == "__main__":
    main()
