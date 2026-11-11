# Brand Radar

A local web app for Eurpac: every spirits brand extension labeled the way Kristin Henderson labeled
by hand, with two predictions for next year (still viable? growing?). Built on the pipeline in
`../brand_scoring_extension/`.

## Run it (first time)

    pip install streamlit plotly openpyxl        (pandas, pyarrow, scikit-learn come with the pipeline)
    python app/build_app_data.py        from the Code folder; writes app/data/*.parquet (about a minute)
    cd app
    streamlit run app.py                opens in your browser at http://localhost:8501

After that, just `streamlit run app.py`. Re-run `build_app_data.py` when new NIQ data arrives.

## Pages

| Page | What it does |
|---|---|
| Home | The numbers at a glance (they follow the floor) and where to go |
| Brand List | Every scored brand above the floor, ranked. Filters: category, price tier, label today, years of data, minimum chance viable, minimum chance growing, supplier, search, in two groups with a Clear button. Rank by growing, viable, size or how far the brand is beating its category (Sales vs category: the brand's cases this year / last year, divided by its category's; 1.00 = keeping pace). Filters are remembered when you switch pages. Click a row to open the brand. Pin the top N to the watchlist. Top 10 per category. Excel download |
| One Brand | Weekly chart (sales and shelf, 13-week average: the view the labels are read from) under a sales-and-shelf scorecard (vs its own best, vs a year ago, vs its category), the label at each year-end and why (hover a year-end dot, or read the list under the chart); a step-through of any year's label; optional category-average overlay; other lines in the same family; pin to watchlist |
| Supplier List | One row per supplier (NIQ's brand owner), added up from its brands above the floor: brands, cases, sales vs a year ago, growing and viable today, best bet. A chart of the top 15 by label. Search, rank, minimum brands. Click a row to open the supplier. Excel download |
| One Supplier | One supplier's numbers, its weekly sales, its brands by label and by category, and a scroll box of every brand it owns (click a brand to open it; a switch adds its brands under the floor). "Open on the Brand List" filters The Brand List to that supplier |
| How Labels Work | What is measured, the three yes/no questions, worked examples, and the category comparison |
| How the Model Works | The two questions (viable, growing) and how to read a chance; how the predictions held up on 2025 (a year the models never saw); the five approaches; what the models lean on; strength by category; the size floor |

Every page except How Labels Work has a collapsed "What am I looking at?" box at the top, and hover help on columns and numbers.

**Sidebar:** pages grouped as Brands, Suppliers and How it works; the size floor on Home, the Brand List and the Supplier List (default 500, remembered as you move between pages; it hides
small brands from the Home numbers, The Brand List and the Supplier List; it does not change the category comparison, which is fixed in step 2, and it does not retrain anything) and the watchlist on every page (pin from The Brand List or One Brand, download as text).

**The chances are calibrated** (step 6, D23): 0.65 means about 65 in 100 brands like this one. Growing is part of viable, so viable is never the smaller number: the two models are fit separately, and where growing comes out higher, build_app_data.py lifts viable to match.

## Files

    app.py                 the router: sets up the seven pages, in three groups
    views/                 home.py, list.py, brand.py, suppliers.py, supplier.py, rules.py, model.py
    common.py              data loading, colors, header, sidebar pieces (floor, filters, watchlist), shared CSS
    build_app_data.py      runs pipeline steps 1, 2, 6 and writes data/
    data/                  predictions.parquet, labels.parquet, weekly.parquet, suppliers.parquet (NIQ data: do not share outside the team and Eurpac)
    assets/                logos (drop smu_logo.png here to replace the text mark)
    .streamlit/config.toml colors

## Planned

- v2: market page (category trends, where growing brands cluster), backtest explorer, score history per brand.
- v3: upload new NIQ files, relabel, retrain, rescore, with a before/after check on the hit rates.
- Hosting: an internal Eurpac machine or their own cloud account, so the data stays theirs.
