"""
STEP 3: Validate the automated labels against the human truth sets.

The only human labels that exist today are Kristin's 112 VODKA brands (single-extension
families, judged at the end of the data, January 2026). So right now every number this
file prints is a vodka-only comparison, and vodka is also the set Devin tuned the rule
thresholds on. The whiskey truth set, once we hand-label it, is the independent test.

For each truth set, label the same brands with our rules as of the end of the data and compare:

    Validation 1   her four tiers vs ours       (agreement by tier)
    Validation 2   her viable 1/0 vs ours       (agreement, balanced accuracy: her paper's metric)

Run the whole file. You get `summary` (one row per truth set) and `matches`
(one table per truth set: her label, ours, and the reason, for every brand).
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
from step01_load_data import load_sales  # noqa: E402
from step02_label import COLUMNS, RULES, TIERS, VIABLE, YEAR_ENDS, apply_rules, features, weekly_tables  # noqa: E402

TRUTH_SETS = {                                   # name: file, in order of trust
    "vodka (tuned on)": config.TRUTH_DIR / "vodka_single_ext_truth_set.csv",
    "whiskey (independent)": config.TRUTH_DIR / "whiskey_single_ext_truth_set.csv",
}
AS_OF = 2025                                     # she judged brands at the end of the data


def load_truth(path):
    t = pd.read_csv(path)
    t["truth_label"] = t["truth_label"].astype(str).str.strip().str.lower().replace({"bankrupt": "discontinued"})
    t = t[t["truth_label"].isin(TIERS) & (t["ALC BRAND EXTENSION"] != "JJ PFISTER VODKA")]
    return t.rename(columns={"ALC BRAND EXTENSION": "brand"})[["brand", "truth_label"]].reset_index(drop=True)


def validate(truth, tables, name):
    f = features(tables, YEAR_ENDS[AS_OF]).reindex(truth["brand"])
    f["label"], f["reason"] = apply_rules(f, **RULES)
    m = truth.assign(label=f["label"].to_numpy(), reason=f["reason"].to_numpy())
    m["truth_viable"] = m["truth_label"].isin(VIABLE).astype(int)
    m["viable"] = m["label"].isin(VIABLE).astype(int)

    print(f"\n{'=' * 70}\n{name}: {len(m)} hand-labeled brands, judged at the end of {AS_OF}\n"
          f"Everything below compares ONLY these brands, in this category.\n{'=' * 70}")
    print("\nValidation 1: of the brands she called each tier, how many did we call the same?")
    agreed = (m["label"] == m["truth_label"])
    by_tier = pd.DataFrame({"brands": m.groupby("truth_label").size(),
                            "we_agreed": agreed.groupby(m["truth_label"]).sum()}).reindex(TIERS)
    by_tier.loc["All brands"] = [len(m), agreed.sum()]
    by_tier = by_tier.astype(int)
    by_tier["rate"] = (by_tier["we_agreed"] / by_tier["brands"]).map("{:.1%}".format)
    by_tier.index.name = "Kristin said"
    print(by_tier.to_string())
    print("\nFull table (rows = Kristin, columns = ours):")
    print(pd.crosstab(m["truth_label"], m["label"]).reindex(index=TIERS, columns=TIERS, fill_value=0))

    print("\nValidation 2: viable (stable + growing) = 1, low performance (decline + discontinued) = 0")
    print(pd.crosstab(m["truth_viable"], m["viable"], rownames=["Kristin"], colnames=["ours"], margins=True))
    tier_agree = (m["label"] == m["truth_label"]).mean()
    bin_agree = (m["viable"] == m["truth_viable"]).mean()
    bal_acc = ((m["viable"][m["truth_viable"] == 1] == 1).mean() + (m["viable"][m["truth_viable"] == 0] == 0).mean()) / 2
    print(f"agreement {bin_agree:.1%}   balanced accuracy {bal_acc:.1%}   (her published model: about 84%)")

    print("\nDisagreements (what the rules saw):")
    miss = m[m["label"] != m["truth_label"]]
    for r in miss.itertuples():
        print(f"  {r.brand:<28} Kristin: {r.truth_label:<13} ours: {r.label:<13} {r.reason}")
    same_binary = (miss["truth_viable"] == miss["viable"]).sum()
    print(f"\n  {len(miss)} disagreements on tier. {same_binary} of them still agree on viable/not; "
          f"{len(miss) - same_binary} flip the 1/0.")
    return m, {"truth_set": name, "brands": len(m), "tier_agreement": round(tier_agree, 3),
               "viable_agreement": round(bin_agree, 3), "balanced_accuracy": round(bal_acc, 3)}


if __name__ == "__main__":
    sales = load_sales(columns=COLUMNS)
    tables = weekly_tables(sales)
    matches, rows = {}, []
    for name, path in TRUTH_SETS.items():
        if not path.exists():
            print(f"\n{name}: no file yet ({path.name}). Label it with step04_label_kit.py.")
            continue
        truth = load_truth(path)
        if truth["truth_label"].eq("").all() or truth.empty:
            print(f"\n{name}: file exists but has no labels yet.")
            continue
        matches[name], row = validate(truth, tables, name)
        rows.append(row)
    summary = pd.DataFrame(rows)
    print(f"\n{'=' * 70}\nSUMMARY (for the paper)\n{'=' * 70}")
    print(summary.to_string(index=False))
