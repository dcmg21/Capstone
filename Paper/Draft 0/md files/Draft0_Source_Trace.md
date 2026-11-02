# Draft 0 - Source Trace

Every factual claim in `Nunnally_Streeter_Introduction_Draft0.md`, mapped to where it came from.

**Status column:**
- **VERIFIED** = I opened the PDF and read the passage myself.
- **SECONDHAND** = the claim comes from another paper's summary of that source, not the source itself. By the professor's Sept 8 rule, these must be read directly or cited as "as cited in."
- **THIN** = from an abstract or search result, not the full text.

**Page numbers:** I give the section name first, since that is the most reliable way to find it. "PDF p." is the position in the file; "printed p." is the number on the page, where they differ.

---

## FILE KEY - which citation is which file

All of these live in `Paper\Sources\`.

| Cited as | Actual filename on disk | Have I opened it? |
|---|---|---|
| **Victory et al.** | `How Do New Products Perform An Investigation.pdf` | Yes, fully |
| **Henderson & Sadler** | `Kristin_Henderson_Journal_Paper.pdf` | Yes, fully |
| **Boone et al. (2018)** | `2017 - Boone - Can Google Trends Improve Your Sales Forecast.pdf` | Yes, fully |
| **Jiang et al. (2020)** | `Demand Forecasting for Alcoholic Beverage Distribution.pdf` | Yes, fully |
| **Cui et al. (2018)** | `2017 - Cui - The Operational Value of Social Media Information.pdf` | Yes, fully |
| **Bronnenberg & Sismeiro (2002)** | `Using Multimarket Data to Predict Brand.pdf` | Yes, fully |
| **Michis (2023)** | `Retail distribution evaluation in brand-level sales response models.pdf` | Yes, fully |
| **Arora et al. (2020)** | `Demand Forecasting In Wholesale Alcohol Distribution.pdf` | Yes, fully |
| **Ford et al. (2020)** | `Automated Machine Learning Framework for Demand Forecasting.pdf` | Yes, fully |
| **Skenderi et al. (2024)** | `Multimodal Forecasting of New Fashion Product Sales with Image-based Google Trends.pdf` | Yes, fully |
| **Kumar et al. (2022)** | `Multimodal Neural Network For Demand Forecasting.pdf` | Yes, fully |

**Two filename traps to watch.** The three alcohol-forecasting papers have nearly identical titles: **Arora**
is the one with "In Wholesale Alcohol Distribution," **Jiang** is "for Alcoholic Beverage Distribution," and
**Ford** is "Automated Machine Learning Framework." And the Boone and Cui files are named 2017 but both
publish as 2018.

---

## Paragraph 1 - The hook

| Claim in our draft | Source | Where exactly | Status |
|---|---|---|---|
| Half of new line extensions gone within a year; 80% within three | Victory et al. | Results, "Failure rate" (PDF p.14, printed p.11) and Table 1 (PDF p.24, printed p.21). Table 1 TOTAL/MEAN row: Q1 32, Y1 50, Y2 64, Y3 80 | **VERIFIED** |
| "across nearly 37,000 new products" | Victory et al. | Methodology, "Data source and scope" (PDF p.10, printed p.7): "36,994 NLEs introduced in five consumer categories" | **VERIFIED** |
| 72% never reached their category's average market share | Victory et al. | Results, "Market share" (PDF p.16, printed p.13) and Table 2 (PDF p.24, printed p.21) | **VERIFIED** |
| Typical new product captured ~0.3% market share | Victory et al. | Results, "Market share" (PDF p.15, printed p.12) and Table 2 | **VERIFIED** |
| A product performing poorly in year one almost never recovers | Victory et al. | Implications (PDF p.22, printed p.19): "if a consumer goods NLE is performing poorly in the first year, it is unlikely to markedly improve its performance in the second and third year" | **VERIFIED** |

---

## Paragraph 2 - Why it matters

| Claim in our draft | Source | Where exactly | Status |
|---|---|---|---|
| More than 22,000 brand extensions in one megacategory, one market | Henderson & Sadler | Section 3.1, Data Source and Structure (PDF p.5): "22,495 unique brand extensions across 8,739 brand families" | **VERIFIED** |
| Most new products underperform their own category average | Victory et al. | Same as paragraph 1 above | **VERIFIED** |
| Everything else in this paragraph | (our own argument) | Not a factual claim needing a citation | n/a |

---

## Paragraph 3 - Current state  ** ALL ELEVEN PDFs NOW OPENED. Paragraph rewritten. **

| Claim in our draft | Source | Where exactly | Status |
|---|---|---|---|
| Retail structure accounts for ~25% of cross-market variance; removing it degrades prediction 35% | Bronnenberg & Sismeiro (2002) | "The Spatial Variance Structures" (PDF p.9, printed p.9): "approximately 69% of the cross-sectional variance in α is distance based, 25% is related to retail structure and conduct." 31% figure for dynamic shocks on PDF p.10. The 35% on Table 3 (PDF p.14) | **VERIFIED** |
| Sales-distribution relationship is nonlinear and often concave, so distribution shows diminishing returns | Michis (2023) | Estimation results (PDF p.8-9, printed p.373-374) and Fig. 1. **CORRECTED:** Kristin's summary claims he shows weighted beats numeric distribution. He does not test that; he asserts it as motivation (PDF p.7) | **VERIFIED, claim corrected** |
| Search interest reduces out-of-sample forecast error 2 to 8% | Boone et al. (2018) | Introduction (PDF p.1, printed p.1770) and Table 2 (PDF p.4): improvements 2.21% to 7.66% across five SKUs | **VERIFIED** |
| Social media improves daily forecasts 13-23%, but only with nonlinear models | Cui et al. (2018) | Abstract (PDF p.1) and Fig. 5 (PDF p.12). Linear-model failure on PDF p.15, printed p.1763. **Caveat: 1-to-7-DAY horizon, online apparel retailer** | **VERIFIED** |
| Google Trends substitutes for absent sales history; most informative signal 7-10 months pre-launch | Skenderi et al. (2024) | Correlation analysis (PDF p.9, printed p.9): strongest lags in range 42-30 weeks. Results Table 1 (PDF p.11). **Caveat: absolute WAPE ~55%, so errors stay large** | **VERIFIED** |
| Multimodal gains ~7%; liquor among worst-forecast categories | Kumar et al. (2022) | Abstract (PDF p.1): 7.37% average SMAPE improvement. Table 2 (PDF p.14): LIQUOR,WINE,BEER 21-22% SMAPE vs 7-9% for bread/dairy. **CORRECTED: Kumar forecasts categories WITH history, not new products** | **VERIFIED, claim corrected** |
| Arora: no "one size fits all" model | Arora et al. (2020) | Abstract (PDF p.2) and Conclusion (PDF p.19, printed p.18), verbatim phrase. Spirits: Taaka Vodka, Jack Daniel's, South Texas | **VERIFIED** |
| Jiang: no single model best across products | Jiang et al. (2020) | Conclusions (PDF p.21, printed p.20): "no one model that performs best overall" | **VERIFIED** |
| Ford: some series were white noise, no model beat a simple mean | Ford et al. (2020) | Conclusion (PDF p.24, printed p.23) and Table 2 (PDF p.19). Products are all spirits: whiskey, tequila, vodka | **VERIFIED** |

---

## Paragraph 4 - The gap

| Claim in our draft | Source | Where exactly | Status |
|---|---|---|---|
| 7.3M observations, 46,008 UPCs, 22,495 extensions | Henderson & Sadler | Section 3.1 (PDF p.5) | **VERIFIED** |
| Hand-labeled truth set of 112 brands | Henderson & Sadler | Section 4.1.1 (PDF p.8): "112 brands: 29 discontinued, 30 decline, 28 stable, and 25 growing" | **VERIFIED** |
| Up to 85% balanced accuracy | Henderson & Sadler | Abstract (PDF p.1) and Table 6 (PDF p.19). **Table 6 is the one that matters: MCDA LV = 85%, binary logistic = 84%** | **VERIFIED** |
| Stable up to 18 months | Henderson & Sadler | Abstract (PDF p.1) and Table 7 (PDF p.20) | **VERIFIED** |
| Four tiers: discontinued, decline, stable, growing | Henderson & Sadler | Section 4.1.1 (PDF p.8) | **VERIFIED** |
| 93% adjacent accuracy | Henderson & Sadler | Section 5.3.2 (PDF p.19): "in 104 of 112 cases the predicted tier was within one step" | **VERIFIED** |
| Four criteria defined, only demand momentum implemented | Henderson & Sadler | Section 4.2.1 (PDF p.10): "The framework includes four criteria... This study implements the demand momentum criterion" | **VERIFIED** |
| The three are category context, **distribution coverage**, promotional efficiency | Henderson & Sadler | Section 4.6, Planned Framework Extensions (PDF p.15). **This is where "headroom" was our error** | **VERIFIED** |
| Category context is the priority; declining brand in declining category | Henderson & Sadler | Section 6.4, Future Work (PDF p.27) | **VERIFIED** |
| Social trend data named as a candidate input | Henderson & Sadler | Section 6.4 (PDF p.27) and Conclusion (PDF p.28) | **VERIFIED** |
| ARIMA named as the path forward | Henderson & Sadler | Section 6.4 (PDF p.27) | **VERIFIED** |
| Simple regression forecast inflated estimates on near-zero brands | Henderson & Sadler | Section 4.3.3, Forecast-Based Alternative (PDF p.13) | **VERIFIED** |

---

## Paragraph 5 - Problem statement

| Claim in our draft | Source | Where exactly | Status |
|---|---|---|---|
| Victory asks whether you can pick a winner at launch | Victory et al. | Limitations & Future Research (PDF p.23, printed p.20): "do 'successful' NLEs that remain in the market for longer also have greater sales performance as early as their launch? This would identify whether it is possible to 'pick' a winner at launch" | **VERIFIED** |
| Henderson & Sadler implement one of four criteria | Henderson & Sadler | Section 4.2.1 (PDF p.10) | **VERIFIED** |

---

## What this leaves you

**All eleven PDFs opened. Every claim in the draft now traces to a passage I read.** No secondhand
citations remain anywhere in the Introduction.

**Two corrections came out of it**, both in paragraph 3, both inherited from Kristin's lit review summary:
- **Michis does not show weighted distribution beats numeric distribution.** He asserts it and uses
  weighted only. What he does show is that the curve is concave, which is better for us anyway.
- **Kumar does not forecast products with no sales history.** That is Skenderi. Kumar forecasts
  established categories.

**Only three open items remain, all citation metadata, none of them factual:**
- Victory year (nothing on the SSRN title page; the 2021 *Marketing Letters* companion avoids the issue)
- Skenderi volume and pages (your PDF is the arXiv preprint, not the journal version)
- Henderson & Sadler journal, volume, year (ask Kristin)

---

## Notes on the year question

The Boone PDF header (PDF p.1) reads: "Vol. 27, No. 10, October 2018, pp. 1770-1774" alongside "© 2017 Production and Operations Management Society" and "Received: June 2017; Accepted: October 2017." The copyright and acceptance dates are 2017; **the publication is 2018**. Boone's own reference list (PDF p.5) cites Cui as 2018, same issue. Cite both as 2018.
