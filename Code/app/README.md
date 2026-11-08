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
| The List | Every scored brand above the floor, ranked. Filters: category, price tier, label today, years of data, minimum chance viable, minimum chance growing, search. Rank by growing, viable or size. Filters are remembered when you switch pages. Click a row to open the brand. Pin the top N to the watchlist. Top 10 per category. Excel download |
| One Brand | Weekly chart (cases and store coverage, 13-week average: the view the labels are read from) with the label at each year-end and why (hover a year-end dot, or read the list under the chart); optional category-average overlay; other lines in the same family; the three yes/no questions and today's three numbers in a collapsed box; pin to watchlist |
| The Model | The two questions (viable, growing) and how to read a chance; how the predictions held up on 2025 (a year the models never saw); the five approaches; what the models lean on; strength by category; the size floor |

Every page has a collapsed "What am I looking at?" box at the top, and hover help on columns and numbers.

**Sidebar:** the size floor on Home and The List (default 250, remembered as you move between pages; it hides
small brands everywhere, it does not retrain anything) and the watchlist on every page (pin from the List or Brand page, download as text).

**The chances are calibrated** (step 6, D23): 0.65 means about 65 in 100 brands like this one. Growing is part of viable, so viable should be the bigger number; the two models are separate, so rare small disagreements can happen.

## Files

    app.py                 the router: sets up the four pages
    views/                 home.py, list.py, brand.py, model.py
    common.py              data loading, colors, header, shared CSS
    build_app_data.py      runs pipeline steps 1, 2, 6 and writes data/
    data/                  predictions.parquet, labels.parquet, weekly.parquet (NIQ data: do not share outside the team and Eurpac)
    assets/                logos (drop smu_logo.png here to replace the text mark)
    .streamlit/config.toml colors

## Planned

- v2: market page (category trends, where growing brands cluster), backtest explorer, score history per brand.
- v3: upload new NIQ files, relabel, retrain, rescore, with a before/after check on the hit rates.
- Hosting: an internal Eurpac machine or their own cloud account, so the data stays theirs.
