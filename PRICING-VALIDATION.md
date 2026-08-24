# Pricing Validation — 24 Bishop Street, Natick MA 01760

**Purpose.** An independent audit of the pricing thesis in `index.html` (the internal
CMA prepared 21 Aug 2026). This document (1) reconstructs the thesis, (2) checks every
number mechanically, (3) tries to prove it wrong through adversarial review and public
research, and (4) ends with a defensible recommendation, a confidence range, and the
facts that must still be verified in MLS/private records before anything goes to a seller.

**Method note.** Every figure inside `index.html` was treated as a *claim to verify*, not
as fact. Internal arithmetic is machine-checked by `scripts/verify_pricing.py` (128 checks,
all passing). External claims were checked against public web sources only; MLS PIN and the
Natick assessor portal could not be independently queried, so anything sourced solely to
them is marked UNVERIFIABLE and listed as a seller/MLS gate at the end.

Audit date: 24 August 2026. Public-source retrieval date: 24 August 2026.

---

## 1. The thesis, reconstructed

### 1.1 Subject (as claimed in the artifact)
| Field | Town record card (FY2026) | Agent walkthrough claim (20 Aug 2026) |
|---|---|---|
| Address / parcel | 24 Bishop St · 31-0000215C | — |
| Lot | 41,579 sf (0.9545 ac); land line carries a **−10% "Restricted/Nonconforming"** factor | back lot at the end of a shared drive |
| Year built | 1996 | — |
| Style | Cape / "Raised Cape", 1.5 story | three usable finished levels |
| Living area (GLA) | **1,532 sf** | **1,832 sf** marketed (twin's MLS basis, "borrowed", never measured) |
| Baths | 1 full + 1 half | **2 full + 1 half** (2nd full bath unrecorded) |
| Heat | Oil, warm air | oil idle; electric wall convectors room-by-room + 1 mini-split (unpermitted) |
| Deck | replaced under permit 2007 | ~480 sf screened/awninged; finish failed |
| Assessment FY2026 | **$812,100** (land $469,000 + building $343,100), +6.9% YoY | — |
| Permits, ever | one (2007 deck) | upper level + electrical + 2nd bath all unpermitted |
| Last interior assessor visit | **25 Jul 2003** | — |

### 1.2 Value conclusion
- **As-is fair value: $815,000** · defensible range **$795,000–$835,000**
- **Normal-condition value: $850,000** (after ~2% cosmetic spend)
- **Recommended list: $799,000 as-is**, or **$849,000 after the work**

### 1.3 Four valuation methods
| Method | Result | Role in conclusion | Stated error |
|---|---|---|---|
| A · Assessment ratio (1.207× prior-year assessment) | **$917,000** | treated as *ceiling*, set aside | median 6.7% |
| B · Paired/mirror sale (22 Bishop, $675K 2021, adjusted) | **$792,000** as-is / $835K done | treated as *low check* | range $758–826K |
| C · Adjusted six-comp grid, reconciled to 2 anchors | **$814,000** | **lead method** | — |
| D · Price per sq ft ($463 × 1,832) | **$848,000** | blunt check | median 8.7% |

### 1.4 The six-comparable grid (as-is indicated values)
| Comp | Sold | $ | Sq ft | Indicated (as-is) |
|---|---|---|---|---|
| 14 Hardwick Rd *(anchor)* | 2026-08-05 | 825,000 | 1,849 | **797,000** |
| 3 Oxbow Rd *(anchor)* | 2026-04-24 | 840,000 | 1,820 | **831,500** |
| 120 Hartford St | 2025-07-01 | 870,000 | 1,840 | 851,500 |
| 28 Barnesdale Rd | 2026-05-28 | 925,000 | 2,003 | 861,500 |
| 5 Longview St | 2026-06-18 | 935,000 | 1,840 | 897,000 |
| 143 Howe St *(dated floor)* | 2025-11-05 | 705,000 | 2,017 | 683,500 |

Adjustment rates (from the section-04 footnote): market +0.15%/mo · living area $170/sf ·
lot $0.90/sf (±$25K cap) · year built $5K/decade (±$24K) · garage $6K/bay · full bath $10K ·
half bath $5K · surplus bedroom −$8K · plus subject-specific curb, permits/records, heating,
and shared-drive/abutting-rental lines.

### 1.5 List strategy
"Search-bracket" / just-below pricing: list at **$799,000** (below the $800K search cap) to
maximise buyer-pool visibility and invite competitive bidding; the doc cites 10 of 20
comparable sales closing over ask. After ~2% cosmetic work, list **$849,000** (below the
$850K cap).

---

## 2. Mechanical arithmetic check — PASS

`scripts/verify_pricing.py` re-derives every published figure from the embedded data
(`window.__D__`, `window.__G__`). **128 checks, all pass.** Confirmed:

- Every comp's net adjustment = Σ(line items); gross = Σ|line items|; indicated = sold + net;
  net % and gross % correct; $/sf = sold ÷ sf — for **both** as-is and work-done states.
- Living-area adjustments equal (1,832 − comp sf) × $170; time adjustments equal
  sold × 0.15%/mo × months. Both rate schedules are applied consistently.
- Reconciled value = mean of the two anchors = (797,000 + 831,500)/2 = **$814,250 → $814,000**.
- Median of six adjusted = **$841,500**; adjusted range **$683,500–$897,000**. All correct.
- Method D = $463 × 1,832 = **$848,016 → $848,000**. Correct.
- Method A = 1.207 × FY2025 assessment. FY2026 $812,100 is "+6.9%", so FY2025 = 812,100/1.069
  = $759,683; × 1.207 = **$916,936 → $917,000**. Internally consistent.
- Mirror house (Method B): $675,000 + line items = **$792,300 as-is** / **$834,700 done**;
  sensitivity at +20/25/30% = $758K/$792K/$826K as-is. All correct. The +25% midpoint =
  $168,750 ≈ the $169,000 "market movement" line.
- Land $/sf: $469,000/41,579 = **$11.28**; $480,490/23,553 = **$20.40**. Correct.

**Conclusion: the artifact contains no arithmetic errors.** The disputes below are about
*inputs, method weighting, and framing* — not math.

---

## 3. Adversarial review — trying to prove it wrong

Findings are ranked by materiality. Each states the challenge, the verdict after
investigation, and the correction carried into the customer artifact.

### 3.1 ★ The conclusion sits at the conservative edge of its own evidence — MATERIAL
The as-is value of **$815,000** is the mean of the **two lowest-indicated non-dated comps**
(14 Hardwick $797K, 3 Oxbow $831.5K). For context, across all six comps:
- mean of six = **$820,333**
- median of six = **$841,500**
- three of four methods sit *above* $815K: A $917K, D $848K, and the six-comp median $841.5K;
  only B ($792K) sits below.

So the headline is ~$5K below the six-comp mean and ~$26K below the six-comp median.

**Is the anchor pick defensible?** Partly yes. The stated rationale is legitimate appraisal
practice: 14 Hardwick is the closest in size (1,849 vs 1,832 sf, +0.9%) and freshest
(closed 16 days prior); 3 Oxbow is the only repeat sale in the dataset (the source of the
time rate) and is closely sized (1,820 sf). An appraiser *would* weight those two heavily.
**But** it is also true that those same two happen to be the two lowest non-dated indications,
so the reconciliation leans down. A central-tendency reconciliation of all six would land
nearer **$835–842K as-is**.

**Correction for the seller artifact:** present $815K as the *conservative, strategy-anchored*
end of an as-is range, not as "the value." State plainly that most methods and five of six
comps point higher (~$820–842K), and that the recommendation to list at $799K is a *tactic*,
not a ceiling. This is the single most important reframing for a seller-facing document.

### 3.2 ★ The 1,832 sq ft basis is unverified and load-bearing — MATERIAL (but newly corroborated)
Every $/sqft figure (Method D $848K, the "$445/sf" headline), and the grid's living-area
adjustments, rest on GLA = **1,832 sf** — a figure the doc admits is *borrowed from the twin's
old MLS listing and never measured*. The town says **1,532 sf** — a ~300 sf / ~20% gap.
Sensitivity of Method D alone: 1,532 sf → $709K; 1,582 → $732K; 1,832 → $848K; 2,030 → $940K.
A quarter-million-dollar swing rides on this one number.

**New corroboration (public records):** the adjacent twin, **22 Bishop Street, is listed at
1,832 sqft, 3 bd / 2 ba, 0.99 ac, built 1996** on Trulia/Compass. The two houses are
described as sharing an identical footprint and identical recorded GLA, so 1,832 is a
*reasonable* basis — but it is still the twin's number, not 24 Bishop measured.

**Correction:** keep 1,832 as the working basis, disclose it prominently as *unmeasured*,
show the value's sensitivity to it, and make a $300–400 professional measurement the first
pre-listing action. Do **not** bury this in a checklist.

### 3.3 ★ Appraisal-gap risk on unpermitted finished area — MATERIAL, under-emphasised
The doc markets 1,832 sf that includes finished space the town doesn't recognise, then admits
(section 07) "the appraiser will not count [unpermitted finished area] … so the upper level
supports no value on paper." These are in tension: if a lender's appraiser measures only the
permitted/above-grade area, a financed buyer could face an **appraisal gap** at $799K–$849K.
The doc treats this as a permits *timeline* risk; for a seller it is also a *net-proceeds*
risk. **Correction:** state the appraisal-gap risk explicitly and tie it to the "pull as-built
permits + measure the house" actions.

### 3.4 "You won't see me deduct for the driveway twice" vs a −$16K line on every comp — WORDING
Section 02 promises the −10% land factor is "already inside every valuation number … which is
why you will not see me deduct for the driveway a second time later on." Yet section 04 applies
a **−$16,000 "shared drive & abutting rental"** line to all six comps.

**Verdict:** not a true double-count. In a comp grid you adjust the *comps* down for their
superior street access to equate them to the subject; that is the *first* application of the
penalty, not a second one, and it is independent of the assessment-ratio method where the −10%
is baked in. **But the sentence is misleading** given the visible −$16K line. **Correction:**
drop the "never twice" promise; explain the shared-drive adjustment plainly and once.

### 3.5 "Flat market" (+0.9%/yr) vs +25% over five years in the mirror house — needs explaining
Section 03 characterises Natick as flat (+0.9%/yr, +2.4% on the one repeat sale). The mirror
house applies **+25% over 2021→2026 (~4.6%/yr)** — a 5× higher rate. On its face this looks
inconsistent.

**Verdict:** reconcilable, but the doc never says how. The appreciation was **front-loaded**:
MA single-family rose steeply in 2021–2022, then flattened 2024–2026 (see §4). So +25% across
five years *and* ~flat in the last year are both true. **Correction:** say this explicitly, and
note that the grid (months-long time adjustments) is more reliable than the mirror house
(five-year index) precisely because of this — which the doc already concludes, for the right
reason once stated.

### 3.6 Market-time-to-offer expectation looks conservative — MODERATE
The doc expects "45–60 days to an accepted offer." Public trackers show Natick going under
agreement in **~18–23 days** (Redfin 01760 = 20 days). The doc's own "55 days" is *list-to-
closing* (which includes the ~30–45 day escrow), so 55 is fine as a list-to-close figure — but
"45–60 days **to an accepted offer**" is much slower than public data suggests for a correctly
priced home. This is consistent with the doc's general conservative lean. **Correction:** frame
expected time-to-offer as "often within a few weeks if priced to invite competition," with
45–60 days as a slower-case, not the base case.

### 3.7 The mirror-house 2021 sale closed *below* ask — MINOR
Public records confirm 22 Bishop sold **$675,000 against a $700,000 list** (−$25K) on
28 Jul 2021. The doc calls it "a valid arm's-length sale" (true) but doesn't mention it was a
below-ask trade. Immaterial to the adjusted result but worth a footnote for candor.

### 3.8 "Comps between 1,688 and 2,017 sq ft" — MINOR FACTUAL SLIP
The six chosen comps range **1,820–2,017 sf**; none is 1,688 sf. The "1,688" in section 04
prose matches no comp in the data. Cosmetic, but it is an internal inconsistency. **Correction:**
state the true range (1,820–2,017) or omit.

### 3.9 Method A "most accurate" yet discarded — DEFENSIBLE
A ($917K) is labelled the most accurate (6.7% error) but set aside as a ceiling. The justification
(assessment ratio assumes normal presentation + street presence, which this back-lot as-is house
lacks) is sound. Compared to the *normal-condition* $850K figure rather than the as-is $815K,
A's $917K is +7.9% — about one median error high. **Verdict:** treating A as a ceiling is
reasonable; but a seller should see that the most accurate method points to $850K+ once the
house presents normally.

### 3.10 Seller-agency / incentive check — FRAMING
A pattern of "value conservatively → list below value → rely on bidding" can serve an agent's
interest (faster, more certain sale) over a seller's (top dollar). The doc's supporting evidence
is genuinely strong (10/20 comps over ask; the $799K captures the sub-$800K cohort), and the
tactic is a recognised one (§4.5). **But** the seller must understand it is a *bet on multiple
offers*: if competition doesn't materialise, an offer near $799K could net below the ~$815–840K
supportable value. **Correction:** present list-below-value as a strategy *with its downside*,
never as free money.

---

## 4. External corroboration (public sources, retrieved 24 Aug 2026)

| # | Claim in CMA | Verdict | What public sources show |
|---|---|---|---|
| 4.1 | MA single-family +20–30% (midpoint +25%) Jul 2021→Aug 2026 | **CORROBORATED** | Warren Group median $540K (Jul 2021) → ~$665–678K (mid-2026) = **+23–26%**; FHFA MA HPI implies up to +30–35%; Zillow ZHVI ~+20–26%. +25% is well inside the band, mid-to-conservative. Appreciation front-loaded 2021–22, flat 2024–26. |
| 4.2 | Natick "flat", $/sqft ~+0.9% YoY | **CORROBORATED** | Redfin 01760 $/sqft $461 (+0.2% YoY); Steinmetz spring-2026 $446 (−1.3%). Essentially flat. |
| 4.2b | Natick single-family median ~$1.10M | **PARTIALLY** | Public all-homes medians run lower (~$870–915K incl. condos); SF-only trends ~$1.0–1.14M. Plausible for SF-only, not independently pinned. |
| 4.2c | "List to closing 55 days" / "45–60 days to an offer" | **PARTIALLY / see 3.6** | Public *days-on-market* ≈18–23 (list-to-pending). 55 is defensible as list-to-*close*; the 45–60 "to an offer" looks conservative. |
| 4.3 | Assessments $812,100 / $824,000 / $983,600 | **UNVERIFIABLE** (public but not automatable) | Natick WebGIS assessor portal is interactive-only; values not machine-retrievable. Pull the three Property Record Cards manually (Assessor 508-647-6420). |
| 4.4 | 22 Bishop sold $675K on 28 Jul 2021 (also $510K 2016, $415K 2007) | **CORROBORATED (exact)** | Trulia/Compass price history confirms all three dates and prices. Note: $675K was **$25K below** the $700K list. Public specs: 1,832 sf, 3bd/2ba, 0.99 ac, built 1996 — corroborates the 1,832 GLA basis and the twin's 2-full-bath count. |
| 4.5 | Just-below-bracket pricing ($799K vs $815K) works | **PARTIALLY** | Concept is standard, recognised practice (Redfin, HomeLight): search-filter bracketing + left-digit/charm effect widen buyer visibility. Specific *magnitude* claims rest on practitioner blogs, not peer-reviewed housing studies. |

Sources: Warren Group (thewarrengroup.com, Jul-2021 and Apr-2026 releases); FHFA HPI via
housingalmanac.com/state/massachusetts; Zillow ZHVI MA; Redfin Natick and 01760 market pages;
Steinmetz spring-2026 Natick report; Trulia/Compass 22 Bishop St price history; Redfin/HomeLight
pricing-psychology explainers. All retrieved 24 Aug 2026.

---

## 5. Three pricing hypotheses

| Hypothesis | As-is value | Launch | Expected outcome | What would falsify it |
|---|---|---|---|---|
| **Conservative** (doc's case) | ~$800–815K | list **$799K** as-is | offers $795–830K; competition brings it toward $815–830K | Sits >60 days (overpriced/thin pool) **or** bids blow past $840K (underpriced) |
| **Evidence-centre** (recommended) | **~$820–840K** (point ~$825K) | list **$799–815K** as-is | offers $815–845K in a normal-competition market | Appraisal <$800K; or buyer pool proves as thin as feared and no bidding appears |
| **Ambitious** (post-work) | normal-condition **$845–865K** | do ~2% work, list **$849K** | offers $830–870K | Cosmetic work fails to shift "project" perception; appraisal gap on unpermitted GLA kills financed offers |

The three are not mutually exclusive — Conservative and Ambitious are the doc's two launch
options; Evidence-centre is my correction to its *valuation* (not its list tactic).

---

## 6. Second-pass adversarial review (of my own conclusion)

- *Am I just talking the number up?* Checked against the downside: five of six comps and three
  of four methods sit above $815K, and the two anchors are demonstrably the two lowest non-dated
  indications. The upward correction is evidence-driven, not optimism. But I keep the *list*
  recommendation conservative because the back-lot/shared-drive/thin-pool risk is real and the
  bidding tactic is sound — so my correction moves the *valuation* up while leaving the *launch
  price* where the doc has it. That is the honest split.
- *Does the 1,832 correction cut the other way?* Yes — if a measurement comes back near 1,532,
  the Evidence-centre value drops materially and the doc's conservatism is vindicated. That is
  exactly why the measurement is gate #1 and why the artifact must not present any $/sqft number
  as settled.
- *Is the "front-loaded appreciation" reconciliation (3.5) just hand-waving?* Public data (4.1)
  supports it: MA gains were concentrated in 2021–22 and flattened after. It is a real pattern,
  not a rationalisation.
- *Residual risk I cannot retire:* all six comp records, the 453-sale aggregates, the backtest
  error figures, 23 Porter Rd, and the "42% price under a bracket" stat are MLS-only. If any are
  materially off, the grid moves. I hold moderate confidence *conditional* on those inputs.

---

## 7. Defensible recommendation & confidence

- **As-is supportable value: $815,000–$840,000** (point estimate **~$825,000**). The doc's
  $815K is the conservative floor of this range, appropriate as a *strategy anchor* but likely
  a slight understatement of realisable value.
- **Normal-condition value (after ~2% cosmetic work): $845,000–$865,000** (point **~$852,000**).
- **Launch price:** the doc's two options are both sound — **$799,000 as-is** or **$849,000
  after the work** — *provided the seller understands each is a below-value tactic betting on
  competition, with a downside if bidding doesn't appear.*
- **Confidence: MODERATE**, conditional on the MLS/assessor inputs and, above all, on the
  unmeasured 1,832 sf GLA. Internal arithmetic: HIGH (128/128). External market backdrop
  (appreciation, flat local market, the twin's sale): CORROBORATED. Comp-level MLS data:
  UNVERIFIED.

---

## 8. Facts Zev must verify in MLS / private records before sending

1. **Measure the house.** Independent floor-plan/GLA measurement. *Highest priority* — the whole
   $/sqft layer and much of the value ride on the unmeasured 1,832 sf.
2. **Confirm the six comps in MLS PIN** — sale price, close date, list price, DOM, condition, and
   living-area basis for 14 Hardwick, 3 Oxbow, 5 Longview, 28 Barnesdale, 120 Hartford, 143 Howe.
3. **Confirm the 453-sale aggregates and the backtest error figures** (median $1.10M, $460/sf,
   size-band $837K, 55-day list-to-close, 6.7% / 8.7% method errors).
4. **Confirm 23 Porter Rd** ($899,900 → $820,000, 62 days) and the "42% price under a bracket" stat.
5. **Pull the three Property Record Cards** (24 Bishop, 22 Bishop, 6 D St) from the Natick WebGIS
   assessor portal to confirm $812,100 / $824,000 / $983,600 and the −10% land factor.
6. **Confirm permit / unpermitted-area exposure** with the Natick Building Department, and the
   resulting appraisal-gap risk on a financed sale.
7. **Confirm current tenancy at 22 Bishop** and have the shared-driveway easement language
   (Bk 26455 Pg 361) ready as a listing attachment.

*The customer-facing artifact (`index.html`) presents only figures that survive this audit, labels
the unmeasured GLA and the MLS-sourced comps as such, and frames the launch price as a strategy
with a stated downside rather than as certainty.*
