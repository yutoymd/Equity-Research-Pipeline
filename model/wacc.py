"""
model/wacc.py

Computes Weighted Average Cost of Capital (WACC) for Qnity Electronics.

WACC = (E/V * Cost of Equity) + (D/V * Cost of Debt * (1 - Tax Rate))

where E = market value of equity, D = market value of debt, V = E + D.

ALL INPUTS BELOW ARE SOURCED AND DATED -- this is deliberate. A DCF is
only as defensible as its assumptions; every number here should be
traceable to something real, not typed in from memory. Where a company-
specific number isn't available (e.g. Qnity has no 5-year trading
history to compute its own beta), a clearly-labeled comparable-company
proxy is used instead, with the comp and reasoning stated explicitly.
"""

from __future__ import annotations


INPUTS = {
    # --- Risk-free rate ---
    # 10-year US Treasury yield, ~4.7% as of week of Aug 24, 2026.
    # Source: multiple financial news sources (Trading Economics, CNBC),
    # consistent with US10Y trading around 4.7% amid deficit/supply concerns.
    "risk_free_rate": 0.047,

    # --- Equity risk premium ---
    # Standard long-run US equity risk premium assumption used in
    # practitioner DCFs (Damodaran's implied ERP has recently run
    # ~4.0-4.5%; using 4.5% here as a defensible, slightly conservative
    # mid-point). NOTE: this is the one input NOT pulled from a live
    # source tonight -- flagged so it can be refreshed/verified later
    # against Damodaran's current implied ERP figure.
    "equity_risk_premium": 0.045,

    # --- Beta ---
    # Qnity has traded independently only since Nov 2025 -- not enough
    # history for a reliable own-company 5-year beta. Using Entegris
    # (ENTG) as the closest direct comparable (semiconductor materials/
    # process solutions supplier) as a proxy. ENTG 5-year monthly beta
    # ~1.3-1.4 across sources (Yahoo Finance, Google Finance) as of
    # Aug 2026. Using 1.35 as a rounded midpoint.
    "beta": 1.35,
    "beta_source_note": "Proxy from Entegris (ENTG) 5Y monthly beta; "
                          "Qnity itself lacks sufficient trading history.",

    # --- Market value of equity ---
    # Market cap ~$26.4B as of Aug 21, 2026 (Yahoo Finance / stockanalysis.com),
    # ~209M shares outstanding (Morningstar). Cross-checked: these two
    # sources agree with each other; other sources found during research
    # showed different snapshot dates/values due to the stock's high
    # volatility (52-week range $70.50-$177.28), so a single dated,
    # internally-consistent pair was chosen deliberately over averaging
    # conflicting numbers.
    "market_cap": 26_400_000_000,
    "market_cap_date": "2026-08-21",

    # --- Cost of debt ---
    # Weighted average coupon across Qnity's actual issued debt
    # (source: SEC filings / press releases, all dated Aug 2025):
    #   - $1.0B Senior Secured Notes due 2032 @ 5.750%
    #   - $750M Senior Unsecured Notes due 2033 @ 6.250%
    #   - $2.35B Senior Secured Term Loan (floating: SOFR + 2.00% margin,
    #     term SOFR was ~4.3% as of Aug 2026 -> ~6.3% all-in estimate)
    # Weighted by principal amount.
    "debt_tranches": [
        {"name": "Secured Notes due 2032", "principal": 1_000_000_000, "rate": 0.0575},
        {"name": "Unsecured Notes due 2033", "principal": 750_000_000, "rate": 0.0625},
        {"name": "Term Loan (floating, SOFR+2.00%)", "principal": 2_350_000_000, "rate": 0.063},
    ],

    # --- Tax rate ---
    # US federal statutory rate (21%) plus a rough blended state/foreign
    # adjustment given Qnity's heavy international footprint (~88% of
    # sales international per the 10-K). Using 24% as a simplified
    # blended estimate -- a more precise number would require Qnity's
    # actual effective tax rate disclosure, worth refining later.
    "tax_rate": 0.24,
}


def weighted_avg_cost_of_debt(debt_tranches: list[dict]) -> float:
    """Principal-weighted average coupon/rate across all debt tranches."""
    total_principal = sum(t["principal"] for t in debt_tranches)
    weighted_sum = sum(t["principal"] * t["rate"] for t in debt_tranches)
    return weighted_sum / total_principal


def cost_of_equity_capm(risk_free_rate: float, beta: float, equity_risk_premium: float) -> float:
    """CAPM: Cost of Equity = Rf + Beta * ERP"""
    return risk_free_rate + beta * equity_risk_premium


def compute_wacc(inputs: dict = INPUTS) -> dict:
    """
    Returns a dict with the full WACC breakdown -- not just the final
    number, so every intermediate step is visible and checkable.
    """
    total_debt = sum(t["principal"] for t in inputs["debt_tranches"])
    market_cap = inputs["market_cap"]
    total_value = market_cap + total_debt

    equity_weight = market_cap / total_value
    debt_weight = total_debt / total_value

    cost_of_equity = cost_of_equity_capm(
        inputs["risk_free_rate"], inputs["beta"], inputs["equity_risk_premium"]
    )
    cost_of_debt_pretax = weighted_avg_cost_of_debt(inputs["debt_tranches"])
    cost_of_debt_aftertax = cost_of_debt_pretax * (1 - inputs["tax_rate"])

    wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt_aftertax)

    return {
        "market_cap": market_cap,
        "total_debt": total_debt,
        "total_value": total_value,
        "equity_weight": equity_weight,
        "debt_weight": debt_weight,
        "cost_of_equity": cost_of_equity,
        "cost_of_debt_pretax": cost_of_debt_pretax,
        "cost_of_debt_aftertax": cost_of_debt_aftertax,
        "wacc": wacc,
    }


def print_wacc_breakdown(result: dict) -> None:
    print("\n--- WACC Breakdown ---")
    print(f"Market cap (equity value):  ${result['market_cap']:,.0f}")
    print(f"Total debt:                 ${result['total_debt']:,.0f}")
    print(f"Total value (E + D):        ${result['total_value']:,.0f}")
    print(f"Equity weight (E/V):        {result['equity_weight']:.1%}")
    print(f"Debt weight (D/V):          {result['debt_weight']:.1%}")
    print(f"Cost of equity (CAPM):      {result['cost_of_equity']:.2%}")
    print(f"Cost of debt (pre-tax):     {result['cost_of_debt_pretax']:.2%}")
    print(f"Cost of debt (after-tax):   {result['cost_of_debt_aftertax']:.2%}")
    print(f"\nWACC:                       {result['wacc']:.2%}")


if __name__ == "__main__":
    result = compute_wacc()
    print_wacc_breakdown(result)
