# Capstone Project Status - Living Log

**Last updated: 2026-11-02**
This is the single running "where we are" document. It gets updated every session.

---

## Snapshot

- **Project:** Extending the Henderson & Sadler CPG (spirits) brand-opportunity scoring framework for the sponsor, Eurpac.
- **Team:** Drew Nunnally & Devin Streeter.
- **Advisors:** Dr. Bivin Sadler & Kristin Henderson (original authors; names go on the paper).
- **Sponsor/client:** Eurpac. Contact: Jacob Saunders (broker). Scott (acquisitions) and Chaz join from the next call.
- **Course:** MSDS 6210 Capstone, Fall 2026. Instructor: Jacquie Cheun-Jensen, PhD (Jcheun@mail.smu.edu).
- **Code:** `Code/brand_scoring_extension/` (ours, Python, steps 1 to 6). `Code/brand_scoring/` is Kristin's R project, untouched. `Code/devin_playground/` is where the labeling rules came from.
- **Data:** `C:\CapstoneData` on each laptop (NDA; never OneDrive or git). Eurpac approved the local copy.
- **Explainer for Eurpac:** `Team/Eurpac_Method_Guide.html`. **Decision log:** `Code/brand_scoring_extension/DECISIONS.md`.

## The project in one line
Label every spirits brand the way Kristin labeled by hand, prove the labels match hers, then predict which brands will still be viable (and which will be growing) a year ahead, so Eurpac has a list of brands worth a call.

---

## Where we are (2026-11-02)

The pipeline is built and tested end to end, in six steps:

| Step | What it does | Result |
|---|---|---|
| 1 Load | Rebuild the dataset from NIQ's raw feed | 7.3M rows, 22,495 brands; matches Kristin's file exactly |
| 2 Label | Rules copy Kristin's chart-reading; every brand labeled discontinued / decline / stable / growing at each year-end, plus viable (1/0) and a reason | Fully automatic |
| 3 Check vs Kristin | Her 112 hand-labeled vodka brands vs ours | 90% agree on tier, 95% on viable/not (her model: 84%) |
| 4 Check across categories | Label mix by category; July vs January seasonality test | Same mix everywhere; no seasonal bias |
| 5 Predict | Viable next year? Growing next year? Two baselines, logistic regression, gradient boosting, tested on 2025 (never seen) | Viable: 98 of top 100 (random 43, "nothing changes" 84). Growing: 65 of top 100 (random 8, "growing now" 53) |
| 6 Predict for real | Score every brand as of end of 2025, looking at 2026. Chances calibrated (D23) so 0.65 means about 65 in 100 | `predictions` table, ranked by chance of growing |

Key findings: survival is driven by store coverage vs the brand's best; growth by sales vs best plus momentum (quarters in a row near its best). Last year's sales growth alone predicts neither. Rules and models are category-free by construction (every brand judged against its own history).

What we tried and dropped: a growth-threshold label (40%, then calibrated to 10%; abandoned because Kristin's labels are about chart shape, not a growth number); hand-labeling a second category (whoever labels now knows the rules); price and promotion share as inputs (zero importance).

## Decisions in force

- Kristin's four labels, reproduced by rules; her viable/low-performance mapping is the 1/0. We invent nothing about what 1 and 0 mean.
- Brand extension is the unit (Eurpac confirmed 2026-10-19).
- Survival is the headline result; growth is the second question, reported honestly as "better than the obvious rule at the top of the list."
- Size floor: a fixed case count (a percentile does not work, brand sizes are too lopsided). 250 for training and as the default; adjustable by Eurpac in the app, which is what Jacob asked for.
- ROI deferred (Eurpac agrees it is too early).
- Steps 3 to 5 are proof, run once. The yearly run for Eurpac is steps 1, 2, 6. A separate production copy comes at the end.
- Plain words everywhere: code columns, printouts and the guide use the same names (sales vs best, stores vs best, store trend).

## Answered by Eurpac (2026-10-19 call, Jacob Saunders)

- Extensions, not families.
- Survival over growth, both matter; "survival is easier to predict" accepted.
- Eurpac is a broker first: the list is for finding brands to sign and represent in the military channel. Acquisition is a deeper analysis by Scott, not Jacob.
- ROI: important long term, too early now.
- NIQ case = 9-liter case.
- Not asked (for Scott next call): dates for the acquisitions and bankruptcies in Kristin's data; the TDP extract.

## Deadlines

- Draft 2 submitted Oct 26. **Draft 3 (>=20 pages): Nov 15, or Nov 22 if the one-week shift applies; confirm.**
- Next Eurpac touch base: in two weeks (about Nov 2), Chaz and Scott invited; likely weekly after that.
- Immersion Nov 20 (mandatory). Final paper Dec 4. Journal submission Dec 11.

## Done

- [x] Pitch (Aug 31), Research Outline (Sept 7), Draft 0 (Sept 14), Draft 1 (Sept 28), Draft 2 (Oct 26).
- [x] NDA signed; data copied locally; Eurpac approved.
- [x] Steps 1 to 6 built, tested, documented. Eurpac method guide written.
- [x] First Eurpac working call with answers to the open questions.

## Action items / next up

After the Nov 2 demo (Eurpac loved it). Jacob: upload/retrain plus category context would make this round a success.

- [ ] **Category context, for next week's call** (Jacob's ask, Devin's earlier commitment): each extension vs its category, as a fourth ratio next to the three. Exclude weak brands below a floor from the category comparison. Scott's example: RTDs up 16%, bourbon down 5%.
- [ ] **Retrain at 500 cases** and show results next to the 250 baseline (`step05_predict_floor500.py`). Scott: cocktails and seltzers may need higher thresholds than mainstay spirits.
- [ ] **Upload new data and retrain inside the app** (by end of program). Retraining is 5 to 10 minutes, occasional. Guardrails needed.
- [ ] **Supplier view:** a Nielsen manufacturer's full portfolio on one page.
- [ ] Smaller ideas from the call: flag brands growing several years in a row; several brands on one chart; different case minimums per use case (incubation vs acquisition).
- [ ] Weekly Eurpac meetings from now on (Jacob sends invites; Chaz and Scott optional).
- [x] Hosting: stays local for now (decided on the call). If hosted later, their own account (AWS est. under $5 a month); data security is the concern.

- [ ] Category context: add "does the brand beat its own category" (Devin's commitment on the call). Decide whether it is a second label or an extra input.
- [ ] Compare our scores against Kristin's opportunity score (Devin's commitment). Needs her un-anonymized scored file: ask her again.
- [ ] Settle with Devin what "validate beyond vodka" means: step 4's cross-category checks (current position) or hand-labeling whiskey (we decided against).
- [ ] **Draft 3: fix the front of the paper.** Draft 2's sections 3 to 5 describe the current pipeline correctly, but the abstract and introduction still describe the old 40% growth-threshold label, and the lit review has the Draft 1 typos back (duplicate 2.4 heading, "chose sale-growth", "ration"). Rewrite abstract and intro around: rules reproduce the expert's labels, then predict a year ahead.
- [x] **App v1 built: `Code/app/` ("Brand Radar", Streamlit, local).** Home, List (floor slider default 250, filters, search, sort, top 10 per category, Excel export), Brand (chart, year-end labels, three numbers, both chances), Model (results in plain words). Run: `python app/build_app_data.py` once, then `streamlit run app.py`.
- [ ] App: Drew runs it on real data and reviews; get the SMU logo file into `app/assets/smu_logo.png`; pick a final name.
- [ ] App v2: market page, backtest explorer, score history. v3: upload and retrain with guardrails.
- [ ] Ask Jacob about hosting: internal Eurpac machine or their own cloud account.
- [ ] Production copy for Eurpac: steps 1, 2, 6 plus a one-page setup guide and the Excel export.
- [ ] Ask Scott on the next call: acquisition and bankruptcy dates; TDP extract.
- [ ] Keep building toward 20 sources. We have 18.

## Folder map (see README.md at the Capstone root)

- `Code/brand_scoring_extension/` - our code (steps 1 to 6, README, DECISIONS.md). `Code/brand_scoring/` - Kristin's R project, read-only. `Code/devin_playground/` - Devin's labeling experiments.
- `Team/` - this log, `Eurpac_Method_Guide.html`, `CPG_Capstone_Dashboard.html`, `CPG_Capstone_Team_Plan.docx`, `Pitch/`, `Meetings/`.
- `Paper/` - drafts (Draft 0, Draft 1) and `Sources/` (16 PDFs). `Data/` - Kristin's vodka truth set.
- `Course/` - `Syllabus/`, `Templates/`.

---

## Meeting log

### 2026-11-02 - Eurpac demo (Jacob Saunders, Chaz Cahn, Scott; Drew, Devin). Summary in `Meetings/Eurpac_11-02-26_summary.txt`.
Drew demoed Brand Radar. Went well: Don Fulano and G4 Reposado confirmed as real winners; Chaz sees two current clients in the top 10 and would use the list when pitching retailers. Asks: category context as a fourth ratio, retrain at 500, upload and retrain in the app, supplier portfolio view. Decision: stay local for now. Weekly meetings from here. (Wispr Flow's notes label the demo "Streeter"; it was Drew.)

### 2026-10-19 - Eurpac call (Jacob Saunders; Drew, Devin). Recording starts at question 3.
- Q1 unit: **extensions** (from Drew's notes).
- Q2 size floor: Jacob agreed 19 cases was too low and understood the 250. The "10% number" he asked us to send for Chaz is the floor we propose; plan is "exclude the smallest 10% of brands" with the implied case count.
- Q3 survival vs growth: "really going to be both, but survival is more of a priority." Devin: survival is a lot easier to predict; growth is what we are struggling with.
- Q4 what they do with a pick: broker first; find a brand to bring in-house and represent in the military channel; look at who represents it now and why it is failing. Acquisition is a separate, deeper analysis (Scott, maybe Chaz). Scott joins the next call.
- Q5 acquisition dates: not asked.
- Q6 ROI: Jacob: important in the long run, too early, no foundation yet.
- NIQ case = 9-liter case ("Casey Cruz" in the transcript).
- Devin's next steps to Jacob: category context (beat its own category, not just grow); compare against Kristin's opportunity score; validate outside vodka; plug-and-play product version. Noted that we only have "simple and logistic regression" (we also have gradient boosting; show the table next time).
- Cadence: next touch base in two weeks, then likely weekly. Jacob to invite Chaz and Scott.

### 2026-09-08 - Class (Drew & Devin both absent; from recording `Meetings/capstone lecture 9-8.txt`)

**What each draft actually contains (new detail):**
- Draft 0 = the Introduction only. "Your first five paragraphs." Rough draft is fine; she reviews and gives feedback.
- Draft 1 = first run at the Lit Review.
- Draft 2 = Methods + some of your results / what you're thinking for results.
- Draft 3 = Results, Discussion, Conclusion. She calls Draft 3 "the first draft of your final paper."

**What she wants IN the Introduction (important, changes our draft):**
- Open with history or a startling fact. "Did you know..." Hook the reader.
- Then: what is the topic, why it is important, the history, the current state, what the gaps are.
- Optionally a little on methods or who is doing what in this space.
- **End with the problem statement** (how our research helps solve it), because that hands off to the lit review.
- Each question in our outline becomes a paragraph. Can be MORE than five paragraphs; a page and a half or more is fine.

**Lit review guidance:**
- **20 sources minimum, and the lit review should be solid by Oct 18.** (We have 6 so far.)
- The 20 count is across the WHOLE paper, not just the lit review: intro, lit review, and discussion all count.
- If we cite 30, all 30 get in-text citations and go on the reference list. If we read something but never cite it, leave it off entirely.
- Outline needed the first 5 as an annotated bibliography (citation + summary + why it fits). She wants proof we actually read them.
- The paper's lit review is NOT an annotated bib: weave all sources into **theme-organized** paragraphs, multiple citations per paragraph. If we don't have sources for a theme yet, naming the theme is fine so she can course-correct us early.
- Must cover background on BOTH the topic AND the methods, so the reader understands why our method fits. Cite others who used similar methods on similar problems.
- **End the lit review with our hypothesis.** No "Hypothesis" heading needed; it goes in the closing paragraph, framed as "based on all this background, here is what I think will happen."
- **Second-hand citations:** if we find a fact in paper A that A credits to paper B, we must go find B and cite BOTH. Citing only B is technically copying A.

**How to read the papers (her big tip):**
- Read the abstract first to decide if it is worth the time, then the intro, then jump straight to **methods and results**. That is all a lit review needs. Go back for the discussion later if there is time.
- She is posting a "how to read a research paper" PowerPoint with this week's summary.

**Citations and tools:**
- **Pick ONE in-text style and stay consistent**: either numeric square brackets or author-year. Do not mix. **The reference list must be APA.**
- **RefWorks** is free with the SMU account: upload references, auto-generate the bibliography, keep annotations. She strongly recommends it.
- **Purdue OWL** for APA formatting.
- SMU library research guides cover literature reviews, starting research, note-taking, APA, and a data science subject guide.
- **Grammarly is explicitly allowed**, including when it restructures sentences. She equates it to Word's spell/grammar check.
- AI may be used to FIND literature and do citation tracing. Not to write the paper.

**Audience note (useful for how we write):**
- The paper is written for the SMU Data Science Review journal. Readers are already data scientists, so we do not need to explain what logistic regression or time series are. We DO need to explain the spirits/CPG domain, which they will not know.
- Her example papers are pulled straight from the Data Science Review, so past issues are good models.

**Results:**
- Unremarkable results are fine and expected. If it does not work, say so in the discussion and make the future-research section verbose about what we learned.

**Logistics:**
- **Formatting: keep the 2-inch margins.** Someone asked to narrow them; she said no, it is based on the journal template. Also open the journal template to see how to format figures and tables.
- **How to submit drafts: share YOUR Word doc with her** (Word > Share > send her the email). She does NOT send a SharePoint link. Required from Draft 1 onward so she can comment inline. Only final presentations go to a Box link she provides.
- **Meetings: Draft 0 meeting is OPTIONAL** (30 min, she starts posting availability the week of Sept 14). **Drafts 1, 2, and 3 require a meeting.** Draft 1 meeting happens the week of Sept 28.
- Guest librarian **Sylvia Jones** attends the Sept 14 class; she is familiar with this group and will meet with teams on request. Her session covers searching, citation tracing, synthesizing sources, and using AI in research.
- Outline feedback promised back by Fri Sept 11.
- Everything is due AFTER class, never before.
- Other: abstract = 250 words / ~5 sentences, one per section. Discussion = the "so what" (policy, process, future research), no new results, plus ethics. She is a sociologist, APA style. 10 groups in the class.
- **VERIFY:** she said presentation recordings are due Nov 19; our syllabus notes say recording Nov 9 / final presentation Nov 18. Immersion is Fri Nov 20 and that is the only mandatory attendance day. An RSVP survey is coming.
- She is posting the list of everyone's project topics.

### 2026-09-11 - Status update
- Pitch delivered Aug 31; Research Outline submitted Sept 7. Both done.
- Next gate is the Introduction / Draft 0 (due Sept 14). Scoped it above.
- **Verified our claims against Kristin's actual paper. Three corrections:**
  1. The criterion is **distribution coverage**, NOT "distribution headroom." We had the name wrong
     in the team plan, this file, the dashboard, and possibly the pitch deck. Fixed here; check the deck.
  2. The **85% balanced accuracy belongs to the MCDA opportunity score**, not the logistic regression
     (which got 84%). Safe phrasing: the framework separates low-performing from viable brands
     "with up to 85% balanced accuracy."
  3. **"She did no forecasting" is too strong.** She tried a linear-regression forecast and rejected it
     because it inflated growth estimates for noisy near-zero brands, and named ARIMA as the path forward.
- **Her Future Work section explicitly lists all three criteria PLUS social trend data**, and says the
  truth set could extend to 200-300 brands across 2-3 subcategories "with minimal additional effort."
  Our plan is literally her stated future work. Frame it that way; it makes the contribution legible.
- Verified paper figures: ~77M raw observations (2021-2026, 260 weeks) filtered to ~7.3M; 46,008 UPCs;
  22,495 brand extensions; 8,739 brand families; 112 hand-labeled brands; 18 stakeholder families.
  Tiers confirmed as discontinued < decline < stable < growing; 93% adjacent accuracy on the ordinal model.
- Draft 0 now written and sourced: `Paper/Nunnally_Streeter_Introduction_Draft0.md`. 11 references, up from 6.
- **Sources folder verified: 11 PDFs, no duplicates.** The three similarly-titled alcohol-forecasting
  papers (Arora 2020, Ford 2020, Jiang 2020) are distinct studies. Boone and Cui are both **2018**
  (Production and Operations Management 27(10), same issue); the "2017" on the PDFs is the copyright
  line and received/accepted dates, not the publication year.
- **Dropped the Nielsen "85% of new products fail" stat.** The Victory paper we now have directly
  disputes it; published research puts failure nearer 40%, reaching 80% only at three years. Citing
  trade press that our own academic source refutes was a reviewer trap.
- **Key finding for our project, from Victory et al.:** across 36,994 new line extensions, 72% never
  reach their own category's average market share, and a product performing poorly in year one almost
  never recovers. That is the empirical justification for building the category context criterion, and
  the paper closes by asking whether it is possible to "pick a winner at launch" - which is our research
  question, posed as an open problem by an independent source. Lead with that framing.
- **Open: Kristin's paper shows no journal/volume/year.** Ask her how she wants it cited.

### 2026-09-11 (later) - All 11 source PDFs read and verified

Opened every PDF in `Paper/Sources/`. Draft 0 and `Draft0_Source_Trace.md` updated. No secondhand
citations remain in the Introduction. **Two more corrections, both inherited from Kristin's lit review:**
- **Michis (2023) does NOT show weighted distribution beats numeric distribution.** Kristin's summary says
  he demonstrates this; he only asserts it as motivation and uses weighted distribution throughout. What he
  actually demonstrates is that the sales-distribution curve is **nonlinear and often concave**, which is a
  better finding for us because it is what justifies measuring distribution *headroom* rather than level.
- **Kumar et al. (2022) does NOT forecast products with no sales history.** That is Skenderi. Kumar
  forecasts 20 established supermarket categories.

**Three findings worth building the paper around:**
1. **Kumar's liquor/wine/beer category was among the worst-forecast of his 20** (about 21% SMAPE vs 7-9%
   for bread and dairy). Independent evidence that our category is genuinely hard.
2. **Ford et al. found several spirits product series were statistically white noise** - no model beat a
   simple mean. Combined with Arora's explicit "no one size fits all" and Jiang's "no one model performs
   best overall," this is a strong argument that point forecasting individual spirits products is
   unreliable, and therefore that **relative cross-sectional scoring is the right approach**. Paragraph 3
   now ends on exactly that, which sets up our contribution.
3. **Bronnenberg's real numbers:** retail structure explains ~25% of cross-market variance in demand
   intercepts, ~31% in dynamic shocks, and removing it costs 35% of predictive accuracy.

**Nine candidate sources identified** from the reference lists of papers we own, listed at the bottom of
Draft 0. Best two: **Friberg & Sanctuary (2017), "The effects of retail distribution on sales of alcoholic
beverages," Marketing Science 36(4)** - alcohol AND distribution, the most on-point source seen anywhere;
and **Hirche et al. (2021), "Predicting under- and overperforming SKUs within the distribution-market share
relationship," Journal of Retailing** - ML classification of SKUs vs expectation at 83% accuracy, which is
structurally our problem.

### 2026-08-30 - Drew & Devin working session
- Reviewed the pitch slides together; agreed problem/why/team/advisors are good, Data and Method need tweaks (now done).
- Settled the method direction: complete the MCDA framework (category context, distribution coverage, promotional efficiency); treat social/trend data as an optional input, not the centerpiece.
- Discussed the real-world buyer context (military base stores, young price-sensitive buyers) and flagged it as a set of questions for Eurpac rather than assumptions to bake in.
- Agreed to contact Eurpac to start data access and clarify the business target.
- (Transcript had no speaker labels; content captured above.)
