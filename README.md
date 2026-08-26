# Equity Research Pipeline: Qnity Electronics (NYSE: Q)

A coded equity research pipeline -- 3-statement model, DCF, and comps --
built in Python rather than Excel, sourced directly from SEC EDGAR's
primary filing data.

**Status: base case complete.** Data pipeline, 3-statement historicals,
WACC, bull/base/bear DCF, and comps-based cross-check are all built and
reconciled. See `analysis/thesis.md` for the full write-up (rated BUY,
$68 DCF base case / $126-237 comps-implied range).

## Why this company

Qnity Electronics was spun off from DuPont on November 3, 2025, supplying
critical materials (CMP slurries/pads, photoresists, thermal/EMI materials)
used throughout semiconductor and advanced electronics manufacturing.

The thesis tension:
- **Bull case:** standalone strategic focus, exposure to the "processing
  material multiplier" effect as chip manufacturing moves to advanced
  nodes (management states advanced nodes require 3-5x more processing
  material per wafer than legacy nodes), and multi-decade customer
  relationships (avg. relationship with top 10 customers exceeds 30 years).
- **Bear case:** $4.1B in new debt taken on at spin-off, customer
  concentration (top 10 customers = 34% of 2025 net sales; Samsung alone
  11%), and heavy geographic/geopolitical exposure (~88% of sales
  international, ~79% from Asia Pacific, ~33% from China specifically).

Full thesis writeup: `analysis/thesis.md`.

## Why code instead of Excel

This is a deliberate choice, not a default. Reasoning:
1. It's a less common approach than the standard WSP/M&I-style Excel
   model, and it's fully version-controlled and browsable on GitHub.
2. It plays to a CS + finance skill combination rather than being a
   finance-only or CS-only project.
3. It's extensible -- once the pipeline works for one company, adding
   sector comps is cheap.

The risk of this approach (and how I'm mitigating it): a coded pipeline
can produce confidently wrong numbers if the input data is subtly broken.
See "Data reconciliation" below.

## Architecture

​```
data/       -- pulls raw financials from SEC EDGAR (primary source, not
               yfinance/scraped data -- see rationale in data/fetch.py)
model/
  statements.py       -- XBRL tag-fallback logic, historical statement assembly
  derived_metrics.py  -- gross profit, margins, YoY growth, free cash flow
  wacc.py             -- CAPM cost of equity, weighted cost of debt, WACC
  dcf.py              -- 5-year unlevered FCF forecast, terminal value, DCF
  scenarios.py        -- bear/base/bull assumption sets run through the DCF
  comps.py            -- EV/EBITDA cross-check against public peers
analysis/
  thesis.md   -- full written thesis: bull/bear case, valuation, rating
notebooks/  -- scratch/exploration space, not the source of truth
​```

## Data source

All historical financials are pulled from SEC EDGAR's `companyfacts` API
(`data.sec.gov/api/xbrl/companyfacts/`), which returns every XBRL-tagged
fact a company has filed -- the primary source, not a third-party
re-scrape. See `data/fetch.py` for the fetch logic.

## Data reconciliation

Real findings from building this pipeline, documented as they were
discovered rather than smoothed over:

- **FY2025 long_term_debt of $4.1B matches the 10-K's disclosed
  Separation-related debt issuance exactly** ($2.35B term loan + $1.0B
  secured notes due 2032 + $750M unsecured notes due 2033) -- a strong
  internal consistency check between the automated XBRL pull and the
  filing's own narrative disclosure.
- **Qnity's XBRL data does not tag Gross Profit or Operating Income as
  standalone line items.** Confirmed by exhaustively searching all
  available `us-gaap` tags for the company -- no `GrossProfit` or
  `OperatingIncomeLoss` tag exists. Gross profit is computed downstream
  (`model/derived_metrics.py`) as revenue minus cost of revenue.
  "Operating income" in the raw pull uses
  `IncomeLossFromContinuingOperationsIncludingPortionAttributableTo...`
  as the closest available proxy, but this sits AFTER interest expense
  and other non-operating items -- it is NOT a true EBIT figure. Using
  it as such in the DCF caused a real, caught bug (see below).
- **A duration-vs-instant XBRL fact type bug** caused `annual_only()` to
  crash on balance-sheet items (Assets, Liabilities -- "instant" facts
  with only an end date) after being written to handle income-statement
  items (Revenue, Net Income -- "duration" facts with start/end dates).
  Fixed by branching logic on which date fields are present.
- **A DEF 14A-sourced annual fact was silently dropped** by an early
  version of `annual_only()` that filtered strictly on the XBRL `fp`
  (fiscal period) label. NetIncomeLoss's FY2025 annual figure came from
  a proxy statement rather than the 10-K itself and had `fp=None`.
  Fixed by detecting full-year periods based on actual date-range span
  (~365 days) instead of trusting the `fp` label.
- **A missing D&A add-back in the DCF caused a ~2x valuation
  understatement.** The unlevered FCF formula subtracted capex without
  adding back D&A (a non-cash expense already embedded in operating
  income), implausibly showing FY2026 forecasted FCF below FY2025
  actual FCF despite growing revenue -- caught by sanity-checking
  forecast output against known historical actuals.
- **The flawed operating-margin proxy (above) caused a second, larger
  valuation distortion** once the D&A bug was fixed: using a 15.3%
  post-interest margin as if it were EBIT implied a price of ~$38/share
  against an actual trading price of $130+. Replaced with the company's
  own disclosed Adjusted Operating EBITDA margin (30.2%, Q2 2026
  earnings) minus an estimated D&A load, which produced a materially
  more defensible $68 base-case valuation.
- **Investigated extending historicals to pre-2023 via Qnity's Form 10
  registration statement, and found this would not add new years.**
  The Form 10's carve-out combined financial statements only extend
  back to FY2024 (the filing explicitly states Qnity "did not operate
  as a stand-alone entity in 2024" -- implying 2024 is itself the
  earliest carve-out year prepared), and FY2023-2025 were already
  available directly from the 10-K's own comparative columns. True
  pre-2023 data would require pulling DuPont's own historical segment
  disclosures for its "Electronics & Imaging" business unit -- a
  different, harder pull (different CIK, segment- rather than
  entity-level reporting, uncertain disclosure granularity) that was
  deliberately not pursued given the marginal value versus effort.

## Setup

```bash
pip install -r requirements.txt
python3 -m model.statements      # pull and assemble historicals
python3 -m model.derived_metrics # margins, growth, FCF
python3 -m model.wacc            # WACC breakdown
python3 -m model.dcf             # base-case DCF
python3 -m model.scenarios       # bear/base/bull comparison
python3 -m model.comps           # EV/EBITDA cross-check
```

## Sources

- Qnity Electronics FY2025 Form 10-K: https://www.sec.gov/Archives/edgar/data/2058873/000205887326000010/q-20251231.htm
- SEC EDGAR API docs: https://www.sec.gov/edgar/sec-api-documentation
