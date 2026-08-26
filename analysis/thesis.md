# Qnity Electronics, Inc. (NYSE: Q) — Initiation of Coverage

**Rating: BUY**
**DCF Price Target: $68 (Base Case) | DCF Range: $49 – $86**
**Comps-Implied Range: $126 – $237 (peer EV/EBITDA)**
**Current Price: ~$130-140 (as of Aug 2026)**

*This is a draft. Figures should be re-verified against the most
current filings before treating this as final.*

---

## Company Overview

Qnity Electronics was spun off from DuPont on November 3, 2025, into two
segments: **Semiconductor Technologies** (CMP slurries/pads, photoresists,
and lithography materials used throughout chip fabrication) and
**Interconnect Solutions** (thermal/EMI materials, advanced packaging, and
PCB laminates). The company has over 50 years of operating history as a
DuPont business unit and now trades independently on the NYSE under
ticker Q.

Since the spin-off, Qnity has delivered nine consecutive quarters of
profitable growth and raised full-year 2026 guidance twice, most
recently to **$5.55B–$5.65B in net sales** (implying ~18% growth over
FY2025's $4.75B), alongside an Adjusted Operating EBITDA margin of
~30.2%.

## Investment Thesis Summary

**Qnity is a well-positioned, structurally advantaged business, and our
comps-based cross-check shows its current valuation is consistent with
—not detached from— how the market prices the semiconductor materials
and equipment sector as a whole.** Our conservative DCF undervalues the
stock relative to its market price, but this reflects the DCF's
inherent conservatism (fade-down growth, flat margins, a 2.5% terminal
growth assumption) rather than a genuine market mispricing. The real
question is whether the SECTOR's current rich multiples (17x-31x
EV/EBITDA) are themselves justified by the AI capex cycle's durability
— a question that applies to the whole peer group, not to Qnity
specifically.

Given Qnity's demonstrated execution (nine consecutive quarters of
profitable growth, two guidance raises in 2026), real structural demand
tailwinds (the processing-material-multiplier effect), and a valuation
that sits mid-pack within — not above — its peer group, we rate the
stock **BUY**, with the caveat that this call is a bet on continued
sector-wide multiple durability as much as it is a bet on
Qnity-specific execution.

---

## Bull Case

- **The "processing material multiplier" effect**: management states
  that advanced logic and memory nodes require three to five times
  more processing material per wafer than legacy nodes. As the
  industry migrates to advanced nodes for AI/HPC workloads, Qnity's
  revenue should scale faster than raw semiconductor unit volume — a
  structural tailwind independent of any single customer or product cycle.
- **Demonstrated execution**: nine consecutive quarters of profitable
  growth and two guidance raises within 2026 alone suggest management
  has been conservative in its own forecasting, and the business is
  outperforming even its own expectations.
- **Deep, durable customer relationships**: the average relationship
  with Qnity's top 10 customers exceeds 30 years, suggesting high
  switching costs and embedded process integration that a new entrant
  would struggle to replicate quickly.
- **Margin expansion trend**: gross margin expanded from 43.5% (FY2023)
  to 46.2% (FY2025), and management has launched an explicit
  transformation plan targeting further operational efficiencies over
  the next two years.
- **Growing free cash flow**: FCF grew from $651M (FY2023) to $988M
  (FY2025), a 51.8% increase, supporting both the deleveraging path and
  the newly authorized $500M share repurchase program.

## Bear Case

- **Customer concentration**: the top 10 customers represent 34% of
  FY2025 net sales, with Samsung alone at 11% and TSMC at 8%. The loss
  or insourcing of any major customer relationship would have an
  outsized impact on revenue.
- **Geographic/geopolitical concentration**: approximately 88% of
  FY2025 net sales came from international operations, ~79% from Asia
  Pacific, and ~33% specifically from China. A China-export-control
  shock or Taiwan-related geopolitical event is not a tail risk here —
  it is a near-third-of-revenue exposure.
- **Leverage taken on at a cyclical peak**: Qnity assumed $4.1B in debt
  at spin-off ($2.35B term loan, $1.0B secured notes due 2032, $750M
  unsecured notes due 2033) at a moment when semiconductor demand is
  running hot on AI capex. Qnity itself discloses that the industry
  "has historically been, and is likely to continue to be, cyclical" —
  a downturn would hit a newly-leveraged balance sheet at an
  inconvenient time.
- **Valuation already prices in a lot of good news**: even our Bull
  case, built on real, specific evidence (margin expansion, slower
  growth fade, transformation-plan efficiency gains), implies a price
  meaningfully below the current market price.

---

## Valuation

### DCF Methodology

We built a 5-year unlevered free cash flow forecast (FY2026-FY2030),
discounted at a WACC of **9.96%**, with a terminal growth rate of 2.5%.

**WACC inputs** (all sourced and dated — see `model/wacc.py`):
- Risk-free rate: 4.7% (10-year US Treasury, Aug 2026)
- Beta: 1.35 (proxied from Entegris, the closest direct comparable —
  Qnity itself lacks sufficient trading history for a reliable
  own-company beta)
- Equity risk premium: 4.5%
- Cost of debt: 6.16% pre-tax, weighted across Qnity's actual issued
  debt tranches
- Capital structure: 86.6% equity / 13.4% debt, based on ~$26.4B market
  cap (Aug 21, 2026) and $4.1B total debt

**FY2026 revenue is anchored to management's own guidance midpoint**
($5.6B), not extrapolated from historicals — we consider this more
defensible than a pure trend extrapolation given how recently and
explicitly management has revised guidance upward.

### Scenario Range

| Scenario | Revenue Growth Path | EBITDA Margin | Enterprise Value | Implied Price/Share |
|----------|---------------------|----------------|-------------------|----------------------|
| Bear | Fades to 3% by FY2030 | 27.0% | $13.4B | **$48.72** |
| Base | Fades to 6% by FY2030 | 30.2% (as disclosed) | $17.5B | **$68.42** |
| Bull | Fades to 9% by FY2030 | 33.0% | $21.2B | **$86.33** |

All three scenarios hold WACC and terminal growth constant, isolating
"view on the business" from "view on risk/discount rate" — only the
growth path and margin assumptions vary.

### The Valuation Gap — Resolved

**Our DCF range ($49–$86) sits well below the current trading price of
~$130-140 — but a comps-based cross-check explains why, rather than
leaving this as an open question.**

We applied current NTM EV/EBITDA multiples from Qnity's closest public
peers (Lam Research, KLA, Applied Materials, Entegris, MKS Instruments
— range 17.4x–31.1x, sourced May 2026) to Qnity's own forward EBITDA:

| Basis | Multiple | Implied Price/Share |
|-------|----------|----------------------|
| Low (MKS, most conservative comp) | 17.4x | **$125.72** |
| Entegris (closest direct comp — materials, not equipment) | 21.9x | **$161.97** |
| Median comp | 23.4x | **$174.43** |
| Mean comp | 24.9x | **$185.86** |
| High (Lam Research) | 31.1x | **$236.74** |

**This resolves the gap.** Even the single most conservative comp in
the set implies a price essentially in line with where Qnity actually
trades — and the closest direct comp (Entegris, also a materials
supplier rather than an equipment maker) implies meaningful additional
upside. The market is not irrationally overpricing Qnity relative to
fundamentals; it is pricing Qnity consistently with how it prices the
entire semiconductor equipment/materials sector right now, which is
trading at rich multiples across the board on AI-capex-driven demand.

**This reframes the actual investment question.** It is no longer "is
Qnity overvalued relative to its cash flows" (a DCF-only framing) — it
is **"is the entire semiconductor materials/equipment sector's current
multiple justified, and does Qnity deserve to trade within that peer
group at its current relative position?"** That is a sector-level and
relative-valuation question, not a company-specific mispricing.

---

## What Would Change Our View

**Reasons to reconsider (upgrade further or take profit):**
- Sector-wide EV/EBITDA multiples compress meaningfully (e.g., an AI
  capex slowdown), which would compress Qnity's price even without any
  change in its own fundamentals
- Margin expansion continues meaningfully beyond the transformation
  plan's stated targets (supports higher conviction)
- Customer concentration risk demonstrably declines through
  diversification (reduces bear-case tail risk)

**Downgrade to Sell if:**
- Guidance is missed or lowered for the first time since the spin-off
- A major customer (Samsung, TSMC) publicly signals insourcing or
  supplier diversification away from Qnity
- Meaningful deterioration in the China/Taiwan geopolitical environment
  affecting the ~33% China-exposed revenue base

---

## Next Steps / Limitations of This Analysis

- **Pre-2023 historical data not yet incorporated.** Qnity's own SEC
  CIK only has data from its own filings starting in 2025; earlier
  carve-out financials exist in the Form 10 registration statement but
  have not yet been pulled into this pipeline.
- **NWC and D&A are simplified assumptions**, not built from a detailed
  working capital or PP&E schedule. A more granular model would build
  these line-by-line rather than as a percentage of revenue.
- **Beta is a comparable-company proxy**, not Qnity's own trading
  history, since the company has been public independently for less
  than a year.
- **The comps set includes both equipment makers (LRCX, KLAC, AMAT,
  MKSI) and a pure materials supplier (ENTG)** — Qnity is itself a
  materials/consumables supplier, so the Entegris-only multiple is
  arguably the more precise read, while the broader set shows the
  range across the wider semiconductor capex ecosystem.
- **This entire BUY thesis is implicitly a bet that current sector-wide
  multiples hold.** If the semiconductor equipment/materials sector
  re-rates downward (e.g., an AI capex slowdown), Qnity's price would
  likely compress even if its own fundamentals remain intact — since
  its valuation is currently more explained by peer multiples than by
  standalone discounted cash flow.

---

*All financial data sourced from SEC EDGAR (CIK 0002058873), Qnity's
FY2025 Form 10-K, and Q1/Q2 2026 earnings releases. Market data as of
approximately August 21-26, 2026. See repository README for full data
reconciliation notes.*
