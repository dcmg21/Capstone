"""
STEP 4: Do the vodka rules behave the same in every category?

The rules were tuned on vodka. They compare each brand to its own history (its own
best stretch, its own prior year), so they should transfer. Three checks, no hand labels:

    A. Label mix by category at the end of 2025. Similar mixes = rules behave consistently.
       A category that is mostly "decline" when others are not is a flag.
    B. Seasonality. Re-label everyone as of mid-year (July 2025) and see how many labels
       flip vs year-end. Year-round categories (vodka) should barely move. If a summer
       category (prepared cocktails) flips in bulk, the rules are reading the season,
       not the brand. Fix if needed: compare 52 weeks to the best 52, not 13 to 13.
    C. Spot-check PDF: random brands per category with the chart and the label on top.

Run the whole file. You get `mix` (A), `flips` (B), one chart, and a PDF in outputs/.
"""

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
from step01_load_data import load_sales  # noqa: E402
from step02_label import COLUMNS, RULES, TIERS, VIABLE, YEAR_ENDS, apply_rules, features, weekly_tables  # noqa: E402

YEAR_END = YEAR_ENDS[2025]     # week 260, January 2026
MID_YEAR = YEAR_END - 26       # week 234, July 2025
PER_CATEGORY = 8               # brands per category in the spot-check PDF
BRAND = "ALC BRAND EXTENSION"


def label_as_of(tables, week):
    f = features(tables, week)
    f["label"], f["reason"] = apply_rules(f, **RULES)
    return f


if __name__ == "__main__":
    sales = load_sales(columns=COLUMNS + ["period_date"])
    tables = weekly_tables(sales)
    category = sales.groupby(BRAND, observed=True)["ALC CATEGORY"].first().rename(index=str)

    # ---- A. label mix by category -------------------------------------------
    end = label_as_of(tables, YEAR_END)
    end["category"] = category.reindex(end.index).astype(str)
    mix = pd.crosstab(end["category"], end["label"], normalize="index")[TIERS].mul(100).round(1)
    mix.insert(0, "brands", end.groupby("category").size())
    mix["viable_%"] = mix[VIABLE].sum(axis=1).round(1)
    mix = mix.sort_values("brands", ascending=False)
    print("A. Label mix by category, end of 2025 (% of brands; viable = stable + growing)")
    print(mix.to_string())

    ax = mix[TIERS].plot.barh(stacked=True, figsize=(11, 6),
                              color=["#9ca3af", "#f59e0b", "#60a5fa", "#16a34a"])
    ax.set_xlabel("% of brands")
    ax.set_ylabel("")
    ax.set_title("Label mix by category, end of 2025. Similar bars = rules behave the same everywhere")
    ax.legend(loc="lower right", ncol=4)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.show()

    # ---- B. seasonality: mid-year vs year-end ---------------------------------
    mid = label_as_of(tables, MID_YEAR)
    both = end[["category", "label"]].join(mid["label"].rename("label_july"), how="inner")
    both["flipped"] = both["label"] != both["label_july"]
    both["viable_flipped"] = both["label"].isin(VIABLE) != both["label_july"].isin(VIABLE)
    flips = both.groupby("category").agg(brands=("label", "size"),
                                         tier_flipped_pct=("flipped", lambda s: round(100 * s.mean(), 1)),
                                         viable_flipped_pct=("viable_flipped", lambda s: round(100 * s.mean(), 1)))
    flips = flips.sort_values("tier_flipped_pct")
    print("\nB. Same brands labeled in July 2025 vs January 2026: how many changed label?")
    print("   (some change is real; a category far above the rest is reacting to the season)")
    print(flips.to_string())

    # ---- C. spot-check PDF ----------------------------------------------------
    matplotlib.use("Agg")
    config.OUTPUTS.mkdir(exist_ok=True)
    dates = sales.drop_duplicates("week").set_index("week")["period_date"].sort_index()
    pool = end.rename_axis("brand").reset_index().sample(frac=1, random_state=1)
    picks = pool.groupby("category").head(PER_CATEGORY).sort_values(["category", "label"])
    path = config.OUTPUTS / "category_spot_check.pdf"
    with PdfPages(path) as pdf:
        rows = picks.to_dict("records")
        for start in range(0, len(rows), 3):
            fig, axes = plt.subplots(3, 2, figsize=(14, 12), squeeze=False)
            page = rows[start:start + 3]
            for ax_row, b in zip(axes, page):
                for ax, wide, color, name in ((ax_row[0], tables["cases"], "steelblue", "Cases"),
                                              (ax_row[1], tables["acv"], "darkgreen", "%ACV")):
                    s = wide.loc[b["brand"]]
                    ax.plot(dates.loc[s.index], s, color=color, lw=0.4, alpha=0.4)
                    ax.plot(dates.loc[s.index], s.rolling(13).mean(), color=color, lw=1.4)
                    ax.set_ylim(bottom=0)
                    ax.set_ylabel(name, color=color)
                ax_row[0].set_title(f"{b['category']}:  {b['brand']}   ->   {b['label'].upper()}",
                                    loc="left", fontsize=10, fontweight="bold")
                ax_row[1].set_title(b["reason"], loc="left", fontsize=9)
            for ax in axes[len(page):].ravel():
                ax.axis("off")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
    print(f"\nC. Spot-check PDF ({PER_CATEGORY} brands per category): {path}")
