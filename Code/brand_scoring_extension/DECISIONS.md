# Decisions log

What we chose, what we didn't, and why. One entry per decision, oldest first.
Update this whenever we make a methodological choice, so anyone (Sadler,
Kristin, Eurpac, the spring cohort) can see the reasoning without asking us.

| # | Date | Decision | Status |
|---|---|---|---|
| D1 | 2026-09-21 | New work in Python; Kristin's R code stays untouched | Active |
| D2 | 2026-09-21 | Data lives outside OneDrive, at `C:\CapstoneData` | Active |
| D3 | 2026-09-22 | Base dataset is Kristin's prepared spirits file, not the raw 77M rows | Replaced by D8 |
| D4 | 2026-09-23 | No database for now; load data into a DataFrame | Active |
| D5 | 2026-09-23 | Port Kristin's label rules to Python as a verified baseline | Done |
| D6 | 2026-09-23 | Binary label = Option B (forward-looking outcome), not Option A | Active, thresholds open |
| D7 | 2026-09-23 | Project folder named `brand_scoring_extension`, files numbered by step | Active |
| D8 | 2026-09-23 | Build our dataset from NIQ's raw feed ourselves, not Kristin's prepared file | Active |
| D9 | 2026-09-23 | Explore all 5 years before choosing label windows; label at several decision points | Active |
| D10 | 2026-09-27 | Label = beat the category in cases, year over year, 2 years in a row | Replaced by D11 (kept: cases, beat the category) |
| D11 | 2026-09-27 | Three-year windows: Year 1 to 2 = input, decide at end of Year 2, Year 2 to 3 = label | Active, threshold to confirm with Eurpac |
| D12 | 2026-09-27 | Dr. Sadler's 4-step roadmap: cases, growth + label, logistic regression, ROI | Active |
| D13 | 2026-09-27 | Step 3 matches the board exactly: plain growth, invest if Year 2 to 3 growth > 40% | Active |
| D14 | 2026-09-27 | Reorder: labels before EDA, EDA focused on the model; code trimmed | Active |
| D15 | 2026-10-09 | Choose the threshold and minimum by matching Kristin's hand labels, not by picking | Replaced by D16 |
| D16 | 2026-10-11 | Label = Kristin's four tiers reproduced by rules; binary = her viable mapping; growth threshold dropped | Active |
| D17 | 2026-10-11 | No second hand-labeled category. Check the rules across categories automatically instead | Active |
| D18 | 2026-10-12 | Predict both viable and growing next year; train 2022-24, test 2024-25; two baselines, two models; 250-case floor | Active |
| D19 | 2026-10-12 | Step 6 = real predictions for next year, in a variable (no file yet); yearly run for Eurpac is steps 1, 2, 6 only | Active |
| D20 | 2026-10-12 | Tried price, promo share, quarters at best. Kept quarters at best (growing 60 to 65); other two set aside | Active |
| D21 | 2026-10-19 | Eurpac call: extensions confirmed, survival over growth, ROI deferred, 9L case confirmed | Active |
| D22 | 2026-10-29 | Size floor stays a fixed case count (percentile does not work), 250 default, adjustable in the app. App v1 built: Brand Radar | Active |
| D23 | 2026-11-02 | Step 6 chances are calibrated (sigmoid, 5-fold). Ordering unchanged, so step 5 numbers stand. No clamp on viable vs growing | Active |
| D24 | 2026-11-08 | Category context: two new inputs (category_growth, vs_category), measured over the established field (250+ cases a year ago). Labels unchanged | Active |
| D25 | 2026-11-08 | "Declining" with sales up: fix the word, not the rule. Label gloss in the app; a sales guard was tested and parked for Devin | Active |
| D26 | 2026-11-08 | Brand page reorganized around a sales-and-shelf scorecard (vs own best, vs a year ago, vs category). Category shelf trend added to step 2 as context only | Active |
| D27 | 2026-11-09 | Merge of devin and main: category context is D24 only (ratio, fixed 250+ field). App-side difference version removed; sidebar floor (default 500) only controls what is displayed | Active |

---

## D1. New work in Python; Kristin's R code stays untouched

**Options considered**
- Rewrite everything in Python
- Stay in R
- Hybrid: her R stays as-is, our new work in Python  <- chosen

**Why**
Her R code is the reference implementation of a published result. If we
rewrote it and got different numbers, we could not tell whether we had found
her bug or created our own. Keeping it untouched gives us something to check
against. New work goes in Python because that is where we move fastest.

**What it means**
Her code lives in `Code/brand_scoring/`, ours in `Code/brand_scoring_extension/`. Parquet
files are the handoff between them. Anything we port from her code must be
checked against her output (see D5).

---

## D2. Data lives outside OneDrive, at `C:\CapstoneData`

**Why**
The NDA (Section 2) prohibits disclosing the data to third parties. OneDrive
syncs to Microsoft's cloud. Eurpac approved copying the data from their server
to a local drive; they did not approve a cloud copy.

**What it means**
Code is in OneDrive and git. Data never is. `config.py` refuses to run if the
data path looks like a synced folder. `.gitignore` blocks parquet, csv, xlsx
and `outputs/`.

---

## D3. Base dataset is Kristin's prepared spirits file, not the raw 77M rows

**Status: replaced by D8.** Kept here so the history is visible.

**Options considered**
- Raw feed: `data/sales_dataset/`, 77,063,935 rows, every category and market
- Kristin's prepared file: `data/sales_dataset_spirits_weeks/`, 7,334,190 rows  <- chosen

**Why**
The prepared file contains everything our four goals need: all 11 spirits
categories, all 5 years (Jan 2021 to Jan 2026), every sales, price and
distribution measure. It is one consistent market (Total US Liquor Open State),
which Kristin chose for having the most complete coverage. It fits in memory
(about 1 GB).

**What Kristin changed versus the raw feed**
- Kept only `ALC MEGACATEGORY` = TOTAL SPIRITS and `Market Description` = Total US Liquor Open State
- Dropped 5 columns: Market Description, ALC MEGACATEGORY (constant after the filter),
  BRAND HIGH, BRAND LOW (redundant), Period Description (replaced by dates)
- Added 3 columns: `week` (1 to 260), `period_date`, `YearBucket` (52-week blocks, unused by her model)

**Revisit if** we need other markets (xAOC, convenience) or non-spirits.
`load_sales("all")` loads the raw feed.

---

## D4. No database for now; load data into a DataFrame

**Options considered**
- A DuckDB database file
- Load straight into a pandas DataFrame  <- chosen

**Why**
While we are still learning the data, it is easier to see it in Positron's
Data Explorer than to query a database. 7.3M rows fits in memory.

**What it means**
`step01_load_data.py` gives you `sales`. `step04_compare_kristin.py` uses DuckDB internally,
but only as an in-memory calculator: no database file is written.

**Revisit if** memory becomes a problem, or we move to the raw 77M rows.

---

## D5. Port Kristin's label rules to Python as a verified baseline

**Result**
`step04_compare_kristin.py` reproduces her `02_rule_based_labeling.R` output exactly:
17,553 discontinued, 3,886 active, 1,056 steady_decline, matching in all 11
categories.

**What went wrong first, and the lesson**
The first port was wrong. It skipped her step that divides %ACV by 100 (the
data is on a 0 to 100 scale, her thresholds are on 0 to 1), plus four smaller
rule differences. It reported 46.8% of brands viable; the true figure is 17.3%.
We caught it only by comparing against her output.
Lesson: every port gets checked against her numbers before we use it.

**Limitation**
Her results file is anonymized (brand names replaced), so the check compares
counts by category, not brand by brand. The un-anonymized file from Kristin
would allow a brand-by-brand check.

---

## D6. Binary label = Option B (forward-looking outcome), not Option A

**Context**
In the 2026-09-21 meeting Eurpac said they are fine moving away from Kristin's
four tiers (discontinued / decline / stable / growing) to a binary label.
Dr. Sadler framed it as invest / don't invest.

Key point: with no outside ground truth, any label built from sales data is a
rule we choose. The question is which rule matches "worth investing in."

**Option A: collapse Kristin's labels.** Not chosen; kept as a baseline.
- 1 = still active; 0 = discontinued or steady decline
- For: already built and verified (D5); simple to explain
- Against: it describes where a brand ended up, not whether it was worth
  backing. It mostly separates dead brands from live ones. 83% of brands come
  out 0. Large established brands count as 1 even though Eurpac would never
  acquire them. It answers "is it alive," not "should we invest."

**Option B: label by what happened next.** Chosen.
- Pick a decision point (for example, week 156 = Jan 2024) and pretend we are
  Eurpac on that day
- Features come only from before the decision point
- Label comes only from after it: 1 if the brand went on to grow (cases in a
  later window at least X% above the window before the decision point) and was
  still on shelves at the end; 0 otherwise
- For: it matches the investment question. Fully automated, binary, works for
  every category at once, no hand-labeling. The model cannot cheat, because
  features and label come from different time periods. Repeating it at
  several decision points gives more examples.
- Risks: "grew" is a threshold we pick and Eurpac should sign off on it.
  Small brands have noisy percentage growth (1 case to 3 is +200%), so we need
  a minimum size. Brands launched after the decision point cannot be labeled
  at that point.

**Option C: outside labels.** Deferred; used later as validation.
- The 123 acquisitions and 37 bankruptcies in Kristin's results file, or a list from Eurpac
- Best ground truth, but blocked: her file is anonymized
- Plan: once we have it, check whether acquired brands tend to get a 1 under Option B

**Still open** (decide after `step02_eda_time.py`, then confirm with Eurpac)
- Decision point(s): which week(s)
- Window lengths: 52 weeks before vs which 52 weeks after
- Growth threshold: 10%? 25%? 50%?
- Minimum size before the decision point
- Whether to exclude large established brands
- Category context: "grew 25%" is easier in a booming category (Prepared
  Cocktails roughly doubled its summer peak 2021 to 2025) than in a shrinking
  one (Vodka, Whiskey). Should growth be measured relative to the brand's
  own category? Seen in step02, cell 2. This is Kristin's unbuilt
  "category context" criterion.

---

## D7. Project folder named `brand_scoring_extension`, files numbered by step

**Why**
This is the second phase of Kristin's project, so the name says what it
extends. Files are numbered in the order you run them (`step01_...`,
`step02_...`) so the workflow reads top to bottom in the folder. The `step`
prefix, rather than a bare number, keeps each file importable in Python.
Replaces the earlier `scoring_py/` layout with its `src/` and `notebooks/`
subfolders, which hid the order.

**What it means**
Order: 1 load, 2 explore, 3 our labels (Option B), 4 compare with Kristin.
Kristin's rules sit last because they are only a comparison, not our method.
Only files we use live here. `config.py` has no number because it isn't a step.

---

## D8. Build our dataset from NIQ's raw feed ourselves

**Options considered**
- Use Kristin's prepared file (D3)
- Start from NIQ's raw feed and do the prep ourselves  <- chosen

**Why**
We want every number in our work to trace back to NIQ, not to someone
else's processing. Her prep was simple (filter, add week numbers), so
redoing it costs little and lets us explain every step ourselves.

**What our prep does** (`step01_load_data.py`)
1. Keep `ALC MEGACATEGORY` = TOTAL SPIRITS
2. Keep `Market Description` = Total US Liquor Open State
3. Turn NIQ's week text ("1 w/e 01/23/21") into `period_date` and `week` (1 to 260)
4. Drop the three columns that step 1 to 3 make redundant

Unlike Kristin we keep `BRAND HIGH` and `BRAND LOW`, and we do not create
`YearBucket`.

**Check**
The load prints whether our row count equals Kristin's (7,334,190). If it
matches, our prep and hers select exactly the same data.

---

## D9. Explore all 5 years first; label at several decision points

**What happened**
The first EDA compared only 2023 with 2025. That was a labeling choice made
before exploring, and it ignored 2021, 2022 and 2024.

**Decision**
- Step 2 (EDA) looks at every year, starting with two plots: every
  category's weekly sales, and the biggest brands' growth vs the same week
  a year earlier. More plots get added one at a time, only when needed.
- Terms: a "year" is a 52-week block starting in late January (the data
  starts 23 Jan 2021). YoY % = (this year - last year) / last year.
- The "grew yes/no" labeling moves to step 3, and will judge brands at
  several decision points (for example 2021 to 2023, 2022 to 2024, 2023 to
  2025) instead of one. That uses all the data and gives more examples.

**Why**
We need to see how brands actually move over the full 5 years before
deciding what "grew" should mean.

---

## D10. Label = beat the category in cases, year over year, 2 years in a row

**Status: the "2 years in a row" part is replaced by D11.** Everything else here
(cases as the data point, beating the category, the settings) still applies.

**The rule** (`step03_our_labels.py`)
At a decision point (the end of a year), a brand is **investable (1)** if, in
each of the next 2 years, its cases grew at least THRESHOLD faster than its
category's cases, and it is still selling at the end. Otherwise **0**.
Brands under 52 cases in the decision year are not judged.

**The data point: `Case`**, summed per brand per 52-week year.
- Growth = (this year - last year) / last year
- beat_by = brand growth - category growth (percentage points)
- Beating the category is the same as gaining share of the category

**Why cases, not the other columns**
- `$` mixes in price: a brand that raises prices looks like it is growing
- `Units` counts a 50ml mini the same as a 1.75L bottle
- `%ACV` measures stores carrying it, not how much people buy (use it as a
  predictor later, not as the label)

**Why beat the category, not just grow**
Step 2 showed categories moving very differently (cocktails up, vodka and
whiskey down). Plain growth would mostly reward being in a hot category.
This is Kristin's unbuilt "category context" criterion.

**Why 2 years in a row, not 1**
One good year is often luck (a promotion, one chain picking it up). Two in a
row is sustained, which is what an investor wants. Costs one decision point:
2021, 2022 and 2023 (judged on the two years after each).

**Settings to confirm with Eurpac** (all at the top of step 3)
- THRESHOLD, starting at 0.50 (Drew's call). Step 3 cell 4 shows the count at
  10%, 20%, 30%, 50% and 100% so the choice can be made with the numbers in view
- YEARS_IN_A_ROW (2), MIN_CASES (52), CATEGORY_ADJUST (True; False = plain growth)

**Check later**
Once Kristin sends the un-anonymized file: do the 123 acquired brands tend to
get a 1? If yes, the rule captures something real.

---

## D11. Three-year windows (the professor's suggestion)

**The setup**

| Year 1 to Year 2 | End of Year 2 | Year 2 to Year 3 |
|---|---|---|
| What we already know: the model's **input** | **Decide**: invest or not | What actually happened: the **label** |

Five years give three windows: 2021-2022-2023, 2022-2023-2024, 2023-2024-2025.

**Label:** 1 if, from Year 2 to Year 3, the brand's cases grew at least THRESHOLD
faster than its category's and it is still selling at the end of Year 3.
Only brands with 52+ cases in both Year 1 and Year 2 are judged.

**Why this replaces D10's "two years in a row"**
It cleanly separates what we knew (input) from what happened (label), so the
model cannot cheat: the input is always before the decision, the label after.
D10 defined a label but never said what the model gets to look at.

**Trade-offs we accept**
- The label covers one year, so it is noisier than two years in a row. The
  threshold absorbs some of that.
- A brand needs about two years of history before it can be judged, so very
  new brands (Eurpac's "emerging" interest) are left out. Note as a limitation.

**How we will test a model**
Train on the first two windows, test on the last (2023-2024-2025). A brand can
appear in all three windows, so testing on the latest year is the honest check,
and it is how Eurpac would use it: learn from the past, predict next year.

**Baseline to beat** (step 3, cell 6)
"Brands that beat their category last year will beat it again next year."
Essentially Kristin's demand momentum. A model that cannot beat this adds nothing.

---

## D12. Dr. Sadler's 4-step roadmap (whiteboard)

| Step | What | Where in our code |
|---|---|---|
| 1 | Cases per product for three years in a row | step 3: `cases_year1` to `cases_year3` |
| 2 | Growth Year 1 to 2 (known) and Year 2 to 3 (outcome); label = Year 2 to 3 growth above a threshold | step 3: `growth_last_year`, `growth_next_year`, `investable` |
| 3 | Logistic regression: label ~ b0 + b1 x (Year 1 to 2 growth) | next to build |
| 4 | ROI | later; needs cost or margin data from Eurpac |

**His worked example** (cases, years 1 / 2 / 3):
100 / 200 / 400 (invest), 100 / 200 / 200 (no), 400 / 1,200 / 1,800 (invest),
1 / 1,000 / 500 (no). The last one shows why tiny starting numbers are filtered
out (MIN_CASES): 1 to 1,000 is +99,900% and means nothing.

**To confirm with him**
- Threshold: the board reads "Label = G > 40%" or "60%". It must be under 50%,
  since the +50% product is marked invest.
- His board uses plain growth. Our default beats the category (D10). Plan: run
  his version first (`CATEGORY_ADJUST = False`), then show ours as the improvement.

---

## D13. Step 3 matches the whiteboard exactly; keep it simple

**The label now:** invest = 1 if cases grew **more than 40%** from Year 2 to
Year 3. Plain growth, as on Dr. Sadler's board. Threshold is a setting and can
change.

**Removed for now, to keep step 3 simple:**
- Beating the category (D10). Kept as a later improvement to compare against.
- The separate "still selling" rule. Not needed: a brand that stops selling
  has -100% growth, so it is labeled 0 anyway.
- The threshold chart, category breakdown and baseline cells.

**Check built in:** step 3, cell 4 runs the board's four example products
through our code and reproduces the board: A invest, B no, C invest, D no.

---

## D14. Labels before EDA; EDA focused on what the model needs

**New order:** 1 load, 2 labels, 3 EDA, 4 logistic regression (next), 5 compare with Kristin.

**Why:** the old EDA (bars per category and top 20 brands) described the market
but didn't help the label or the model. Once the label existed, the useful
questions were about it. The EDA now has:
1. Weekly cases by category (kept: the market picture)
2. Distribution of Year 2 to 3 growth with the 40% line, per window (the label)
3. Invest rate by last year's growth bucket (the model's question, previewed)
4. Invest rate by category (table)

**Also:** `year` is now added in step 1 (one place). All files trimmed to
short comments. Kristin's port outputs `kristin_labels` so it never overwrites
our `labels`.

---

## D15. Calibrate the threshold and minimum against the human truth set

**Problem:** 40% and 52 cases were our picks. Someone else could pick 25% and 15.

**Decision:** `step04_calibrate.py` tries every threshold (0% to 100% by 5) and
minimum (0 to 500 cases), labels Kristin's 112 hand-labeled vodka brands with
each, and keeps the combination with the best balanced accuracy against her labels.
The labeling itself stays fully automatic; only the two settings come from this step.

**Choices inside it:**
- Her 1 = `growing` only (the invest question). `growing` + `stable` is the
  "healthy vs dying" version; one line to switch (`POSITIVE`).
- Compared on our last window (2023-2024-2025), since she judged brands at the end of the data.
- Brands under the minimum count as 0 (too small to invest in).

**Caution:** 112 brands, one category, 147 combinations. Expect a range of settings
to score about the same; pick a round value inside that range, not the single top row.

---

## D16. The label is Kristin's, reproduced by rules. No growth threshold.

**What we learned (D15):** calibrating a growth threshold against her hand labels gave
0% to 10% growth as the best match (85% balanced accuracy). So her "growing" was never
about a 40% jump; it was about the shape of the chart. A single growth number is the
wrong tool, and every threshold invites "why not 25%?"

**Decision**
- Label: her four tiers (discontinued / decline / stable / growing), produced by Devin's
  rules on cases-vs-peak, ACV-vs-peak and ACV year-over-year (`step02_label.py`).
  About 90% agreement with her 112 vodka labels in his testing.
- Binary: **her own mapping** from `02_validation_and_modeling.Rmd` and her paper:
  viable (stable + growing) = 1, low performance (decline + discontinued) = 0.
  We invent nothing about what 1 and 0 mean.
- Each brand is labeled "as of" each year-end (data cut at that week). The model will
  predict the label at the end of Year 3 from what was known at the end of Year 2.
- Proof: `step03_check_kristin.py` prints her labels vs ours (4x4), the binary (2x2
  with balanced accuracy, her metric), and a held-out check so we can't be accused of
  memorizing her 112 brands.

**Known limits, and the plan for them**
- Her labels exist only at the end of the data; earlier year-ends are unchecked.
  Offer: hand-label about 30 brands as of end of 2023 if Eurpac wants it.
- Her labels are vodka, single-extension families only. See D17 for how we handle other categories.

**Removed:** step02 threshold label, step03 EDA (built for that label), step04 calibrate,
step05 port of her R rules (verified, but we match her hand labels now, not her rules).
D10 to D15 stay as history.

---

## D17. Check the rules across categories automatically; no second hand-labeled set

**Why not hand-label whiskey:** the rules compare each brand to its own best stretch and
its own prior year, never to a fixed number, so category should not matter for a dying
or a growing brand. And a second hand-labeled set has its own problems: whoever labels
knows the rules by now, and if it disagrees we would be tempted to re-tune. Kristin's
vodka set stays the one human check, said plainly in the paper.

**The real risk is seasonality.** The rules look at the last 13 weeks against the best
13 weeks ever. A summer category (prepared cocktails) is always "far from its best" in
January; a December category (cordials) is always "at its best". That would mislabel
whole categories at year-end.

**What `step04_check_categories.py` does**
- A. Label mix by category at the end of 2025. A category that is mostly decline when the
  others are not is a flag.
- B. Re-label everyone as of July 2025 and count how many labels flip vs January 2026.
  Vodka should barely move. A seasonal category flipping in bulk is the rules reading the
  season, not the brand.
- C. Spot-check PDF, 8 random brands per category with chart, label and reason.

**Result (2026-10-12, real data):** A: label mix nearly identical across the nine big
categories (35-50% discontinued, 30-40% decline, 14-20% stable, 4-8% growing; viable 17-26%).
Non-alcoholic spirits (205 brands, young category) and grain alcohol (22) differ, explainably.
B: tier flips July-to-January 23-30% in every category, cocktails 30 vs vodka 27 vs cordials 28,
so no seasonal bias. Viable flips 10-14%. **No fix needed; 13-week peaks stay.**

**Pros and cons to say out loud**
- Pro: one rule set, every brand judged against itself, fully automatic, every label explained.
- Con: human-validated on 112 vodka brands only. Checks A to C show consistency, not truth.
- Con: possible seasonal bias at year-end; measured by B, fixable if present.

---

## D18. The prediction model (Dr. Sadler's board, step 3)

**Setup:** one row per brand per year. Inputs as of the end of year t: the three rule
numbers, cases (log), cases growth vs the year before, the tier, the category.
Target: viable (stable or growing) at the end of year t+1. Train on 2022->2023 and
2023->2024, test on 2024->2025, which the model never sees.

**Baselines it has to beat**
- "stays the same": next year's 1/0 = this year's. Strong, because most brands keep sliding or keep going.
- "growth only": logistic regression on last year's cases growth alone. The whiteboard version.

**Scoring:** balanced accuracy (Kristin's metric), AUC, and the hit rate in the top 100 and
top 500 brands the model is most confident in. The hit rate is the number Eurpac cares about:
"if you had shortlisted these 100 at the end of 2024, how many were viable a year later?"

**Choices**
- Logistic regression first (explainable coefficients). Gradient boosting only if it clearly wins.
- `class_weight="balanced"` so the 0.5 cutoff is sensible with about 20% positives.
- TARGET is one setting: "viable" (Kristin's 1) or "growing" (closer to "invest"). Confirm with Sadler which is the headline.
- Growth ratios capped at 5x so a 1-case brand going to 100 doesn't dominate.

**Results so far (logistic regression, 250-case floor, test year 2025)**
- Viable: model 97% in the top 100 vs 84% for "stays the same", 61% growth-only, 43% random.
  Works in every category (7-10 of the top 10 each). Driver: stores vs peak.
- Growing: model 52% vs 53% for "stays the same", 19% growth-only, 8% random. The model
  does not beat "pick what is growing now". It also over-picked tequila (learned 2022-24, cooled in 2025).
- Last year's cases growth alone is nearly useless for either question.

**With the new inputs and gradient boosting (test year 2025, top 100):**
- Viable: logistic 96, boosting 95, "stays the same" 84, growth-only 61, random 43. Use logistic.
- Growing: boosting 60, logistic 55, "stays the same" 53, growth-only 19, random 8. Boosting is
  modestly better at the top, a tie at the top 500 (45 vs 46), better AUC (0.88 vs 0.85).
  Claim: "somewhat better than picking what is growing now", no more. One test year.
- Coefficients: one reference level left out per group (discontinued, first category, first price tier).
250-case floor kept, to be set by Eurpac.

**Open:** a brand-family version; more test years as data arrives.

---

## D19. The deliverable and the yearly run

**Step 6** (`step06_predict_next_year.py`) trains both models on every year-to-year step (no
hold-out; the test was step 5) and scores every brand as of the newest year-end. Output is a
variable, `predictions`: brand, family, category, price tier, cases, label today, viable, reason,
chance viable next year (logistic), chance growing next year (boosting), rank overall, rank in
category. Plus `top_per_category`. Nothing is written to disk; the Excel export belongs to the
production copy at the end.

**Feature importance (step 5):** logistic coefficients next to permutation importance for the
boosting model (shuffle one input on the test year, measure the AUC drop), both questions.

**Ranking is by chance of growing**, because the viable chance is highest for giants, which is
correct but not useful. Brands under the 250-case floor are listed but not scored.

**Yearly run for Eurpac:** steps 1, 2 and 6 (step 6 calls 1 and 2). Steps 3 to 5 are validation,
done once for the paper. Year-ends come from the data (`year_ends_in`), so new NIQ files need no
code change. A separate "production" copy with only those three steps can be made at the end.

**Open:** Eurpac to confirm the unit (extension vs family) and the size floor.

---

## D20. Three new inputs, aimed at "which growers keep going"

**Why:** growing is the hard question (60 vs 53). The reasons a brand grows are mostly outside
the data, but three things in the data were unused.

| Input | How it is built | Data check |
|---|---|---|
| price | total $ / total units over the last year, logged | `$` and `Units` are 0% blank |
| promo_share | NIQ's incremental cases / total cases over the last year, floored at 0 | `Incr Case` 0% blank, but it is NIQ's *estimate* (actual minus modeled base) and is negative in many weeks; summing over a year nets that out. Weakest of the three |
| quarters_at_best | quarters in a row, counting back, with the 13-week average at 80%+ of the best so far (max 8) | uses `Case` only |

Pre-computed NIQ price columns (`Avg Unit Price` 21% blank, `Any Promo Unit Price` 63% blank)
are not used; the blanks are zero-sale weeks, and we compute price from totals instead.

**Also:** all column names are plain words now (sales_vs_best, stores_vs_best, store_trend,
store_coverage, cases_last_year, sales_growth, brand_size, brand_age, weeks_of_history).

**Result (test year 2025, growing, top 100):** base inputs 60; + quarters_at_best 65; + all three 68.
Price and promo_share showed zero importance on their own, so the last 3 points are not trusted.
**Kept quarters_at_best** (cases only, easy to explain). Price and promo_share stay computed in step 2
but off the input list. Final with momentum: viable 98 (logistic) / 95 (boosting); growing 65 (boosting) / 51 (logistic).
Per category, growing: vodka 10, tequila 9, whiskey 5 (was 2); cognac, brandy, grain alcohol still 2-3 of 10.
Momentum's permutation importance is tiny (0.002): it helps the top of the list, not the overall ranking.

---

## D21. Eurpac answers (call with Jacob Saunders, 2026-10-19)

| Question | Answer | What changes |
|---|---|---|
| Extension or family? | Extensions | Nothing |
| Size floor? | Jacob agreed 19 was too low and 250 was reasonable; asked for "the 10% number". See D22 for how that resolved | |
| Survival or growth? | Both, survival first; "survival is easier to predict" acknowledged | Lead with the viable result (98 of 100). Growth stays as the second question |
| What do you do with a pick? | Eurpac is a broker first: find brands to sign and represent in the military channel. Acquisition is a deeper analysis by Scott (and maybe Chaz), not Jacob | Frame the list as "brands worth a call", not "brands worth buying". Scott joins the next call |
| Acquisition dates? | Not asked | Ask Scott next call |
| ROI? | Matters long term, too early now | Future work |
| NIQ case? | 9-liter case confirmed | Nothing |

**Committed on the call (Devin):** a category-context measure (does the brand beat its own
category, not just grow), and a comparison against Kristin's opportunity score. Validation
beyond vodka and a plug-and-play version were also mentioned.

**Cadence:** next touch base in two weeks (Chaz and Scott invited), likely weekly after that.

---

## D22. The size floor is a fixed case count, adjustable in the app

**Devin's follow-up to Jacob (2026-10-28):** a percentile does not work because brand sizes are so
lopsided. Bottom 10% by count = under 1 case a year (only removes brands that already stopped).
Bottom 10% of volume = about 95% of all brands (the top 5% sell 90% of the cases). He sent what
each floor keeps: 12 cases ~12,500 brands; 52 ~9,300; 100 ~7,800; 250 ~5,700; 500 ~4,300.

**Jacob's reply:** can the threshold be a parameter in the final dashboard that the end user adjusts,
so if 500 turns out too high it is easy to change.

**Decision:**
- Training floor stays **250** (what step 5 tested and the paper reports). Lives in `step05_predict.py`.
- Scoring goes down to **12** cases so the app has room (`build_app_data.py`, SCORE_FLOOR).
- The app's List page has the floor as a slider, default 250, with the live brand count.
- `prepare_inputs` and `score_latest` take a `min_cases` argument so the two floors are separate.

**App v1 (`Code/app/`, Streamlit, local):** Home, List (slider, filters, search, sort, top 10 per
category, Excel download), Brand (Kristin's chart with year-end labels, the three numbers, both
chances), Model (step 5 results in plain words, importance, floor table). Eurpac colors from their
logo; SMU text mark until the logo file arrives. Working name "Brand Radar".

**Hosting:** data cannot sit on a third party's server, so Vercel/Supabase are out. Options are an
internal Eurpac machine or their own cloud account. Ask Jacob.

---

## D23. Step 6 chances are calibrated

**What we found (Nov 2):** in the app data, the growing chance was higher than the viable chance
for 5,113 of 12,558 scored brands. That cannot be true: growing is part of viable (stable or growing).

**Why:** both models train with `class_weight="balanced"`, which treats yes and no as equally
common. Good for ranking, but it stretches the raw numbers, and it stretches growing's more
(about 5 in 100 brands) than viable's (about 1 in 4). So "chance" was really a score.

**What we did:** step 6 wraps each model in `CalibratedClassifierCV(method="sigmoid", cv=5,
ensemble=False)`. The model is fit on all rows; the calibration learns, from 5-fold predictions,
how its scores map to real yes rates. Sigmoid is a monotone map, so brands keep exactly the same
order; step 5's hit rates and the paper's tables are untouched.

**Not done on purpose:** no clamp forcing viable >= growing. The two models are separate and we
want to see where they disagree, not hide it. Step 6 prints the count; it should be near zero.

**Effect:** "0.65" now means about 65 in 100, which is what the app's tooltips say. Rerun
`app\build_app_data.py` to refresh the app data. Step 5 does not need calibration (it only ranks).

---

## D24. Category context: the brand against its category, as a model input

**Why:** On the Nov 2 call Jacob asked for category context "as a fourth ratio in the probability."
Scott's example: RTDs up 16% while bourbon is down 5%, so the same 10% growth means very
different things in the two categories. Devin added: compare against the field, not the losers.

**What we built (step 2, `category_context`):** two numbers per brand per year-end.
- `category_growth`: the category's cases this year / last year, summed over the **established
  field**: brands with two full years of history that already sold at least 250 cases a year ago
  (`CATEGORY_FLOOR`). Two full years so the category's growth is on the same footing as the brand's
  `sales_growth` (a review on Nov 8 caught that mid-year launches were counting a partial prior year). That keeps
  out new launches (which would make every existing brand look like it is losing ground) and tiny
  brands (which would swamp the count).
- `vs_category`: the brand's `sales_growth` / its `category_growth`. 1.00 = moved with the
  category, 1.20 = grew 20% faster, 0.85 = lost ground.

**What we did not do:** change the labels. The rules match Kristin's hand labels and stay as they
are. The two numbers are extra inputs in step 5's `INPUTS` (filled with 1.0 when there is no prior
year, capped at 5 like `sales_growth`). Step 5 says whether they help; step 6 carries them into the
app, where they show on the Brand page and as a "Vs category" column on the List.

**Result (Nov 8, real data):** viable top-100 unchanged at 98 (logistic) / 95 (boosting); growing 51 / 66
(was 65). Boosting importance for both new inputs is about 0.00, bottom of the list. The logistic
coefficients look large but `vs_category` is `sales_growth / category_growth`, so the two columns carry
nearly the same information and the weight is split between them; the boosting number is the one to
read. Conclusion: a brand's own trajectory already carries the category signal in this data, where
category growth only ranges 0.93 (cognac) to 1.10 (prepared cocktails). Kept as context for the reader
and as a model input (harmless), not as a driver.

**500-case floor (same day, `step05_predict_floor500.py`):** viable 98 / 93, growing 49 / 60, per-category
growing worse (brandy 1 of 10). Pools differ (5,808 vs 4,431 test brands) so not perfectly matched, but
the direction is clear: 500 is not better. 250 stays (closes the "what if 500" question from Oct 19 and Nov 2).

**To run:** step 2, then step 5 for the test numbers and importance, then `app\build_app_data.py`.

---

## D25. "Declining" while sales are up: fix the word, not the rule

**The question (Drew, Nov 8):** Chum Churum Soon Hari Peach is labeled declining at the end of 2025
with sales at 99% of its best and up 16% on the year. Store trend 0.898 (just under 0.90) fired the
"slipping off shelves" rule. Is the rule wrong? Should stores come out?

**Stores stay.** Stores vs best is the strongest predictor of survival by far (boosting importance
0.24 vs 0.01 for sales vs best), Kristin's hand labels are mostly about distribution, and the paper's
main finding is "survival is about stores." Removing stores would break all three.

**How common:** 61 of 2,513 declining labels at end of 2025 over 250 cases (2.4%); 806 of 31,134
across all years (2.6%). About 1% of the brands on the list.

**Evidence gathered on a sales guard** ("not declining if sales >= 80% of best and up on the year;
call it stable"):
- Flipped brands a year later: 52% viable, 18% growing. Stable brands: 54% viable, 7% growing.
  Declining brands overall: 26% viable, 3% growing. So the flipped brands behave like stable brands.
- Robust to the cutoff: every variant tried (70/80/90% of best; growth > 0/5/10%) gives 48 to 56% viable.
- Kristin's 112: no brand affected; agreement stays 90.3% tier, 95.6% viable.
- Step 5 test rerun with the guard: viable 98 / 95 unchanged; growing 50 / 64 vs 50 / 67 (noise);
  "nothing changes" baseline 84 -> 87 (labels more persistent). Neutral for the model.
- G4 Reposado 2023 would flip declining -> stable (sales 90% of best, +36%, stores -36%).
- Mirror case noted, not acted on: stable brands with sales under 60% of best are 41% viable a year
  later vs 61% for other stable brands. The model sees sales vs best, so no second exception.

**Decision:** keep the three questions exactly as they are (they are Devin's, they match Kristin, and
Draft 2 describes them). Fix the word instead: the app now shows what each label measures next to it
(`LABEL_GLOSS` in `app/common.py`): Discontinued = gone from shelves, Declining = losing shelf space,
Stable = holding its shelf, Growing = near its best and adding shelf. The Brand page also gained a
collapsed "step through a year's label" box that recomputes every number from the weekly rows and
explains the sales-up-but-declining case when it occurs.

**Parked for Devin:** the guard is defensible and cheap (one clause in `apply_rules`, one line in the
reason text, step 3 reproof). Adopt only if Devin agrees, since it changes the published rules.

---

## D26. The Brand page is a sales-and-shelf scorecard

**Why:** after D24 and D25 the Brand page asked the reader to assemble the story from a chip, a
sentence, two chart panels, a scaled overlay and a prose hover. Drew: "getting way too confusing."

**The idea:** everything about a brand is sales or shelf, measured three ways: against its own best,
against a year ago, against its category. So the page opens with a two-row table:

| | vs its own best | vs a year ago | vs cordials |
|---|---|---|---|
| Sales | 99% | +41% | cordials -5%, ahead |
| Shelf | 80% | -22% | cordials -4%, behind |

followed by the label with its gloss and the number that fired it. The label visibly comes from the
shelf row. The year-end hover is the same four lines for that year. Chart panels renamed "Sales: cases
per week" and "Shelf: % of stores carrying it." The scaled overlay stays, off by default.

**Step 2 addition:** `category_shelf_trend` (the established field's mean %ACV this year / last year)
and `vs_shelf` (brand's store_trend / that), built exactly like D24's sales version. Context only, not
a model input: tested on Nov 8, importance 0.003 / 0.000, growing top-100 67 -> 65 (noise). Raw store
trend splits next-year outcomes at least as well as the category-relative version.

**Finding worth telling Eurpac:** in 2025 every category's established brands lost shelf: brandy,
whiskey, cognac about -10%, vodka and gin -7 to -8%, tequila -5%, cordials -4%, non-alcoholic flat.
A brand holding its store count in 2025 was beating its field. The models were tested in this same
market, so the chances already reflect it.

---

## D27. One definition of category context (merge of devin and main)

**Decision:** category context follows D24: computed in step 2 (`category_context`), with the
comparison group fixed at brands with two full years of history and CATEGORY_FLOOR (250)+ cases a
year ago. `vs_category` is a ratio, brand / category, where 1.00 = keeping pace.

**Removed:** the app-side version from bbe847c (`with_category_context` / `category_context(floor)` in
`app/common.py`), which measured the gap in percentage points and let the sidebar floor decide which
brands made up the category. Two definitions of the same number would have disagreed on screen.

**The sidebar floor** (default 500) now only controls what is displayed: it hides small brands from the
Home numbers and The List. It does not change the category comparison, the labels or the models.

---

## Open items (not decisions yet)

- Ask Kristin for the un-anonymized results file (unblocks D5 brand-level check and Option C)
- Run step 3 on real data; put the three tables in the paper
- Confirm with Dr. Sadler: predict "viable at end of Year 3" from the end of Year 2
- Delete old `C:\CapstoneData\eurpac.duckdb` and `cache\` if still there
- Ask Scott (next Eurpac call): dates for the acquisitions and bankruptcies; the TDP extract
- Ask Jacob: internal machine or Eurpac cloud account for hosting the app
- Build the category-context measure and the comparison with Kristin's opportunity score (Devin's commitment)

Note: file names in D1 to D13 refer to the old numbering (old step03 = labels, old step04 = Kristin). See D14.
