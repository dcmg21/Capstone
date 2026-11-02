# brand_scoring_extension

Phase 2 of the Eurpac brand-opportunity project (Nunnally & Streeter, Fall 2026).
Extends Kristin Henderson's R project in `../brand_scoring`, which we never edit.
Read `DECISIONS.md` for what we chose and why.

## The story

1. Kristin hand-labeled 112 vodka brands (discontinued / decline / stable / growing) and
   defined the binary: **viable = stable + growing = 1**, low performance = 0.
2. Rules (Devin's) reproduce her four labels from each brand's chart. We prove the match on her 112 (vodka only).
3. The same rules label all 22,000 brands in all 11 categories, at each year-end, automatically. Step 4 checks they behave the same across categories.
4. A model predicts next year's label from this year's, tested on a year it never saw.
5. The models predict next year for every brand on the newest data.

Steps 3, 4 and 5 are proof, run once for the paper. A yearly run for Eurpac is steps 1, 2 and 6
(step 6 calls 1 and 2 itself). Year-ends are read from the data, so new files need no code change.

## The flow

| Step | File | What it does | You get |
|---|---|---|---|
| 1 | `step01_load_data.py` | Builds our data from NIQ's raw feed, checks it against Kristin's | `sales`, `guide`, `check` |
| 2 | `step02_label.py` | Labels every brand as of the end of 2022, 2023, 2024, 2025, plus the 1/0 and a reason | `labels` |
| 3 | `step03_check_kristin.py` | Proof: her 112 vodka hand labels vs ours, by tier and by viable/not | `matches`, `summary` |
| 4 | `step04_check_categories.py` | Do the vodka rules behave the same in every category? Label mix, a seasonality test (July vs January), and a spot-check PDF | `mix`, `flips`, 1 chart, PDF in `outputs/` |
| 5 | `step05_predict.py` | Two questions: viable next year? growing next year? Two baselines, two models, tested on 2024 to 2025, plus what each model leans on | `results`, `top`, `importance` |
| 6 | `step06_predict_next_year.py` | Train on every year, predict next year for every brand as of the newest year-end. Nothing written to disk | `predictions`, `top_per_category` |
| 5b | `step05_predict_floor500.py` | Step 5 again with a 500-case floor, to answer Eurpac's "what if 500" without touching the paper's numbers | same as step 5 |

`config.py` holds the paths. Data lives in `C:\CapstoneData` (NDA). Truth sets live in `Capstone/Data`.
`../devin_playground/auto_label.py` is where the step 2 rules were developed; it stays as is.
`../app/` is the Streamlit app (Brand Radar); `app/build_app_data.py` runs steps 1, 2 and 6 and writes the app's data files.

## Setup (once)

    pip install -r requirements.txt
    setx EURPAC_DATA "C:\CapstoneData"      then restart Positron

## Running in Positron

Open each file and press Ctrl+Shift+Enter. Each step loads what it needs (about 20 seconds).
