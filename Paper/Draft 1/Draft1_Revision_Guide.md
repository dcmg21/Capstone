# Draft 1 revision guide

Prepared September 28, 2026. This is an instructional working guide for Drew Nunnally and Devin Streeter, not manuscript text for submission. Draft 0 has not been changed.

The main revision is a change in the research objective. The September 27 Sadler summary prioritizes automated, forward-looking growth labels and a simple logistic regression proof of concept. Draft 0 still promises completion of the MCDA criteria, external social/search signals, and leave-one-out evaluation. Revise the paper around the current question before expanding the literature review.

## Evidence and scope

- Assignment authority: [syllabus](<C:/Users/Eight/Documents/MSDS/Capstone/Drew_ext/Course/Syllabus/MSDS 6210 Capstone Syllabus Fall 2026.pdf>), especially pages 13 and 14 for Draft 1, page 11 for the restriction on AI-written research papers, and page 20 for submission instructions.
- Current direction: [September 27 meeting](<C:/Users/Eight/Documents/MSDS/Capstone/Drew_ext/Team/Meetings/Sadler_09-27-26.docx>), read with the September 16 and September 20 summaries for context. These are summaries, and example thresholds are not final stakeholder acceptance criteria.
- Starting manuscript: [Draft 0](<C:/Users/Eight/Documents/MSDS/Capstone/Drew_ext/Paper/Draft 0/Nunnally_Streeter_Introduction_Draft0.docx>).
- Permitted scholarly evidence: only the 16 PDFs in [the top-level sources directory](<C:/Users/Eight/Documents/MSDS/Capstone/sources>). Papers cited inside those PDFs are not automatically approved additions.
- Implementation evidence: Drew's current labeling code and decisions log; Devin's saved data audit and outputs. Code was inspected, not changed or executed. Saved EDA results were inspected, not regenerated from raw data.

The older project status log predates the September 27 direction. Its descriptions of Draft 1 and the primary research contribution should not override the syllabus or newer meeting notes.

## What Draft 1 must contain

| Requirement | Evidence from the syllabus | Work needed |
|---|---|---|
| Supplied Word template | Use the provided template without modification, page 13; 10% of grade | Preserve the supplied page setup and styles. Do not change margins to reach a page target. |
| At least five pages | Page 13; 15% | Treat five as the minimum, with enough space for the required sections. |
| Preliminary abstract | Page 13 | Explain the revised objective and planned approach; use explicit placeholders for unavailable results and conclusions. |
| Introduction of two to four pages | Page 13; 10% | Explain the domain, practical decision, prior work, gap, and revised problem statement. |
| Problem statement and advisor | Page 14; 20% | Match the September 27 task and retain accurate advisor attribution. |
| Near-completed literature review | Page 13 | Synthesize themes and compare findings, rather than producing a list of paper summaries. |
| Five more references | Exact rubric wording on page 14; 10% | Track additions and removals. Do not interpret this as five references total. |
| Methods and EDA | Early algorithm, data collection, solution and evaluation sections, pages 13 and 14; 20% | Define the observation, years, eligibility, label, predictor, baseline and proposed evaluation. Include clearly identified preliminary EDA. |
| Other sections outlined | Page 14; 10% | Outline Results, Discussion, Ethics, Limitations, Conclusion and Future Work without inventing findings. |
| Grammar and citation consistency | Page 14; 5%; missing citations/reference list can result in zero | Place citations with the supported sentence, before its final period. Use APA reference entries. |

The syllabus describes the audience as beginning MSDS students with bridge-course knowledge. Explain the spirits domain and the roles of labels, predictors and evaluation. The document must contain connected draft prose, not only notes. The professor needs editing privileges when the Word file is shared; this review has not shared or submitted anything.

Draft 0 uses numbered citations, while the syllabus rubric refers to APA format. The saved class notes permit numeric or author-year in-text citations with APA references. Keep that instructor guidance explicit and use one system consistently. If keeping numbers, renumber by first appearance after the rewrite.

## Reframe the research contribution

Build the problem statement from these components in your own words:

1. **Decision context:** Eurpac needs a repeatable way to screen eligible spirits brands for future growth.
2. **Observed unit:** the current implementation aggregates UPC sales to a brand extension. It does not directly estimate the value of an entire company or acquisition.
3. **Prediction time:** the end of the second 52-week year, when the first two years are available.
4. **Predictor:** case-sales growth from Year 1 to Year 2.
5. **Target:** whether case-sales growth from Year 2 to Year 3 exceeds a specified threshold.
6. **Test:** whether logistic regression improves useful out-of-sample classification over simple baselines.
7. **Business limitation:** a growth label is a screening proxy. Its relationship to investment returns still requires stakeholder information and validation.

The contribution can include a reproducible labeling process, explicit temporal separation of inputs and outcomes, sample-coverage analysis, and threshold sensitivity. Improved predictive performance is a hypothesis to test, not an established contribution.

Automating this new binary target does not reproduce Henderson's four manually assigned trajectory tiers. Those are different definitions. Similarly, a correctly calculated growth outcome is observable under the chosen rule, but calling it "invest" adds an unvalidated business interpretation.

## Changes to Draft 0

| Draft 0 component | Revision instruction |
|---|---|
| Title emphasizes category-context signals | Make the title describe automated outcome labels and prediction of future spirits sales growth. Avoid promising valuation or ROI. |
| Abstract promises added criteria, cross-category truth-set expansion, Google Trends, social interest and LOOCV | Replace those commitments with the current labeling and prediction design. State the actual population that can be studied. |
| Opening uses broad new-product failure statistics | Keep only accurately qualified motivation. Explain the difference between new line extensions in the source and the eligible spirits extensions in this study. |
| Business paragraph promises identification before much history exists | Explain that this baseline needs two years of input history and a third year for retrospective evaluation. It does not solve launch-day or no-history prediction. |
| Distribution paragraph | Retain as domain context or as a reason to examine future predictors. Do not imply distribution criteria are now implemented. |
| Google Trends and social-media paragraph | Remove claims supported only by Boone, Cui and Skenderi because those PDFs are outside the permitted folder. Kumar can support a brief discussion of optional external signals. |
| Alcohol-forecasting paragraph concludes point forecasting is unreliable | Narrow the conclusion to heterogeneous performance and the need for benchmarks. Arora and Jiang also report improvements over naive forecasts. Their findings do not prove classification is superior. |
| Henderson paragraph | Credit the prior framework and its evaluated results, then explain the different label and evaluation task. Avoid describing every future-work component as part of this capstone. |
| Final problem statement promises all three unimplemented criteria | Replace with the focused growth-prediction question and testable hypothesis. Category adjustment can be a later comparison if actually evaluated. |
| Missing sections | Add thematic literature review, data and preliminary EDA, early methods and evaluation, and outlines for later sections. |

For the introduction, organize the reasoning as domain and decision, difficulty and evidence, prior framework, remaining gap, then the present study. Put detailed comparisons of prior methods in the literature review.

## Define the current method precisely

Let C1, C2 and C3 be case totals in three consecutive 52-week blocks. The current code defines:

- Input growth: g12 = C2 / C1 - 1.
- Future growth: g23 = C3 / C2 - 1.
- Binary target: y = 1 when g23 > tau, otherwise 0.
- Current provisional settings: tau = 0.40; C1 and C2 must each be at least 52 cases.
- Planned first model: logistic regression estimating P(y = 1 | g12).

Use the original ratios to describe label assignment. The code rounds displayed growth values, but applies the threshold to the unrounded calculation. Its comparison is strictly greater than 40%, not greater than or equal to 40%.

Distinguish two adjustable thresholds: the sales-growth threshold tau defines the outcome; a probability cutoff determines which model predictions are called positive. Changing tau changes the classification task and normally requires rebuilding labels and refitting the model. Moving a probability cutoff alone does not.

The data's year labels are not calendar years. The saved audit records five 52-week blocks spanning January 23, 2021 through January 10, 2026. Name the dates or block convention so readers do not assume January-to-December totals.

### Reconcile these choices before finalizing Methods

| Choice | Current evidence | How to describe its status |
|---|---|---|
| Growth threshold | Meeting examples are 25% and 50%; current code uses >40% | 40% is the implemented starting setting, not a confirmed investment hurdle. |
| Completeness | Devin requires at least 48 selling weeks with sales of at least $1 in each qualifying year; Drew requires at least 52 cases in each input year | These define different samples. Do not use Devin's counts as Drew's model sample size. |
| Outcome-year eligibility | Devin's complete panel requires a qualifying Year 3; Drew's rule does not | Conditioning on continued Year 3 selling can exclude failures and limit the population to survivors. |
| Missing sales | Drew fills absent brand-year cells with zero | Verify that absence means observed zero sales, not unavailable reporting, before interpreting it as a negative growth outcome. |
| Category adjustment | Earlier decisions discussed it; the current label uses absolute growth | Treat relative growth as a possible sensitivity analysis, not the implemented baseline. |
| Train/test split | September 27 suggests 70/30; decisions log also proposes a chronological holdout | State the actual split used and the prediction question it answers. A final fitted model was not found in the inspected extension scripts. |
| Emerging brands | Current code has a minimum volume, but no clear upper-size or age restriction | Do not call every eligible extension an emerging or acquisition-ready brand. |
| ROI | Meeting calls for additional client input | Outline the required inputs and defer numerical return claims. |

### Evaluation guidance

For a first 70/30 experiment, use a clearly defined cohort and keep repeated brand observations together. A common decision date provides a clearer interpretation than mixing each brand's latest available year. A random split of pooled overlapping windows can place related observations and later information on both sides of the split.

For the claim of predicting a future period, recommend a chronological holdout: earlier eligible windows for training and the last window for testing, with all training outcomes available at the test decision date. Repeated brands across time can match a deployment question about already observed brands; a separate group holdout is needed for a claim about previously unseen brands. These are different questions, and neither score substitutes for the other.

Compare the model with the majority-class baseline and a simple prior-growth persistence rule evaluated on the same rows. Report class counts, confusion matrix, positive-class precision and recall, balanced accuracy, and a precision-recall summary. If reporting probabilities for business use, also examine calibration. Select transformations and probability cutoffs using training or validation data, then reserve the final holdout for evaluation.

Henderson's reported metrics cannot be used as a directly comparable score to beat when labels, population, dates and split design differ. Recompute a suitable baseline on the new task if making a comparative performance claim.

## Preliminary EDA already available

The saved [coverage table](<C:/Users/Eight/Documents/MSDS/Capstone/Dev_ext/outputs/audit_coverage_by_category.csv>) and [audit notebook](<C:/Users/Eight/Documents/MSDS/Capstone/Dev_ext/01_data_availability_audit.ipynb>) provide material for Draft 1, with these qualifications:

- 22,495 total brand extensions appear in the audit. At 48 selling weeks per qualifying year and no additional annual case floor, 8,233 extensions have at least three contiguous qualifying years, or 36.6%.
- The same table reports 6,561 with at least four contiguous qualifying years and 5,357 with all five.
- There are 6,569 eligible windows beginning in block 1, 6,735 in block 2, and 6,847 in block 3. The 8,233 count is unique extensions across eligible windows, not the number in one common test period.
- On each extension's latest eligible window, 817 of 8,233 meet the audit's >=25% growth rule, and 410 meet >=50%. Those are exploratory class-balance results under Devin's filter, not results for Drew's >40% target.
- Eligibility changes materially with the selling-week requirement. The notebook also shows that excluded extensions can differ in initial size and growth, so exclusions need analysis.

Useful manuscript exhibits are an eligibility-flow table, category-level coverage, growth distributions with the chosen threshold, and class balance by window. Report the sample definition in each caption. EDA showing an association between past growth and labels is not a held-out predictive result.

These figures were read from saved outputs. They should be regenerated under the final settings before being presented as the final modeling dataset.

## Literature review themes and permitted sources

Use the following as reading and synthesis prompts. This is source triage, not a finished literature review or an APA bibliography. Numerical claims and reference metadata need a final check against the local PDFs when used in manuscript prose.

| Theme | Papers in the permitted folder | Supported role and limits |
|---|---|---|
| Defining product success and brand opportunity | Victory et al.; Henderson and Sadler; Hirche et al. (2021) | Compare survival, market share, trajectory tiers, and performance relative to distribution. Explain why the present study explicitly chooses future case growth. Hirche's three-class SKU task is not a future investment-return task. |
| Retail and alcohol prediction | Fildes, Ma and Kolassa (2022); Arora et al. (2020); Jiang et al. (2020); Ford et al. (2020) | Establish product heterogeneity, aggregation choices, practical forecasting purposes and simple benchmark comparisons. Discuss positive forecasting results as well as difficult series. |
| Automated labeling and decision criteria | Lam et al. (2026); Ulrich et al. (2022); Henderson and Sadler | Lam studies weak labeling functions for text classification; our outcome is a deterministic rule on future sales. Ulrich classifies which forecast model to select and evaluates inventory-related profitability. Neither validates "invest" labels or supplies an acquisition ROI formula. |
| Category and distribution context | Michis (2023); Bronnenberg and Sismeiro (2002); Dunn et al. (2025); Hirche et al. (2021) | Discuss nonlinear distribution response, cross-market structure, category revenue components and relative SKU performance. Motivate limitations of a single absolute growth rule without promising additional implemented criteria. |
| Learning across products | Lei et al. (2025); Zhu et al. (2021) | Discuss aggregate-to-product information and cross-series learning as alternatives if category-specific samples are thin. Lei uses retail transfer learning; Zhu studies pharmaceutical supply chains. Do not attribute these methods to the simple logistic baseline. |
| Boundaries of sales-only screening | Kumar et al. (2022); Pozner et al. (2022) | Kumar studies news/search signals with historical supermarket demand. Pozner studies consumer ratings and authenticity in craft beer. Use these only for a clearly relevant omission or future-research point, not as evidence of spirits investment returns. |

Five particularly useful new references relative to Draft 0 are Hirche, Lam, Fildes, Ulrich and Dunn. Lei and Zhu offer additional methodological context; Pozner is more peripheral. Include each only where it supports a specific argument.

There are 16 permitted PDFs. Eight overlap Draft 0 and eight are new. Draft 0's Boone, Cui and Skenderi sources are outside this set. Replacing those three and adding the five priority papers would produce 13 references. Using all 16 would give a net increase of five over Draft 0's 11, but relevance must determine inclusion. The rubric does not make clear whether "five more" means five newly introduced works or a net increase of five; do not silently call a 13-reference draft compliant with the stricter interpretation.

For synthesis, each theme should explain the question, compare the relevant studies, identify what they establish and leave unresolved, then connect that gap to this study. Close the review with the proposed hypothesis and evaluation comparison, using your own wording.

## Citation corrections and interpretation limits

1. **Victory, local PDF pages 14 to 16:** 72% below category-average market share refers to the quarter after launch; the corresponding three-year figure is approximately 66%. The paper does not say 72% never reach the average. The reported 0.3% is a mean, with a positively skewed distribution, so avoid calling it the typical product without qualification.
2. **Victory, pages 14 and 15:** reported failure rates are 50% at one year and 80% at three years in the study sample, with a caveat about temporary or seasonal extensions. Excluding products that disappear in the launch quarter changes the reported rates. Do not universalize the finding to all emerging spirits brands.
3. **Henderson, pages 18 to 22:** distinguish approximately 84% balanced accuracy for binary logistic regression, up to 85% for the MCDA score, and 93% adjacent-tier accuracy. Adjacent accuracy allows a one-tier difference. External validation on 18 stakeholder families produced roughly 61% to 63% balanced accuracy. None is a verified ROI or automated-label accuracy estimate for this project.
4. **Hirche:** its reported 83% relates to under-, in-line-, and overperforming SKUs relative to a distribution-market-share curve using the studied scanner data. Preserve its unit and target when using that result.
5. **Lam:** programmatic weak supervision provides context for labeling quality and coverage. A future-sales threshold is a different mechanism, and Expona's text-classification gains cannot be transferred to this study.
6. **Publication dates:** use the issue year supported by the PDF, not simply a filename, acceptance date or copyright line. The supplied copies show Fildes (2022), Ulrich (2022), Michis (2023), Pozner (2022), Lei (2025), Dunn (2025), and Lam (2026).
7. **Unconfirmed metadata:** Henderson's local PDF does not establish a journal issue or publication date. Draft 0's 2026 entry and publication-status wording need confirmation. Verify Victory's year and publication status from the supplied copy or author-provided metadata rather than inventing details.
8. **Source boundaries:** a permitted paper's reference list does not authorize adding its cited works. Cite a review for its synthesis and avoid claiming to have read the underlying studies when they are not in the permitted folder.

## Suggested writing order

1. Settle the target, eligible population, and intended evaluation question. Keep 40% explicitly provisional if describing the current code.
2. Rewrite the title, abstract plan, and final introduction problem statement around those choices.
3. Revise the remaining introduction, correcting the source claims and removing obsolete commitments.
4. Build the thematic literature review from the approved PDFs, keeping new-source and removed-source counts visible.
5. Write Data, Preliminary EDA, and Methods with a clear distinction between implemented steps, saved exploratory findings and planned evaluation.
6. Outline the later sections, including label validity, survivorship, missing-versus-zero sales, minimum history, generalization and financial-data limitations.
7. Audit every in-text citation against the final reference list, then verify the Word template and page count after student-authored text is in place.

No model accuracy, ROI, manuscript submission, or completed final Draft 1 is claimed by this guide.
