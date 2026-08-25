# Equity Research Pipeline: Qnity Electronics (NYSE: Q)

A coded equity research pipeline -- 3-statement model, DCF, and comps --
built in Python rather than Excel, sourced directly from SEC EDGAR's
primary filing data.

**Status: in progress.** This README will grow alongside the analysis.

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

Full thesis writeup: `analysis/thesis.md` (TBD).

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

```
data/       -- pulls raw financials from SEC EDGAR (primary source, not
               yfinance/scraped data -- see rationale in data/fetch.py)
model/      -- 3-statement linking logic, forecast assumptions, DCF
analysis/   -- comps, sensitivity tables, written thesis
notebooks/  -- scratch/exploration space, not the source of truth
```

## Data source

All historical financials are pulled from SEC EDGAR's `companyfacts` API
(`data.sec.gov/api/xbrl/companyfacts/`), which returns every XBRL-tagged
fact a company has filed -- the primary source, not a third-party
re-scrape. See `data/fetch.py` for the fetch logic.

## Data reconciliation

TBD -- once historicals are pulled, I will manually verify at least one
full fiscal year's figures against the actual 10-K filing line-by-line,
documented here. This step exists because automated pipelines can produce
confidently wrong output if a tag is mislabeled or a unit is misread --
catching that here is more valuable than any other single step in this
project.

## Setup

```bash
pip install -r requirements.txt
python data/fetch.py
```

## Sources

- Qnity Electronics FY2025 Form 10-K: https://www.sec.gov/Archives/edgar/data/2058873/000205887326000010/q-20251231.htm
- SEC EDGAR API docs: https://www.sec.gov/edgar/sec-api-documentation
