"""
model/dcf.py

Builds a 5-year unlevered free cash flow forecast and discounts it back
to present value using the WACC computed in model/wacc.py, to arrive at
an implied Enterprise Value, Equity Value, and price per share.

FORECAST ASSUMPTIONS -- sourced and dated where possible:

- FY2026 revenue: management guidance of $5.55B-$5.65B (raised twice in
  2026 after 9 consecutive quarters of profitable growth), midpoint
  $5.60B used. Source: Q2 2026 earnings release, Aug 4, 2026.
- FY2027 onward: growth is faded down from the FY2026 guided rate
  toward a long-run terminal growth rate. This is standard DCF practice
  -- a company cannot sustain above-market growth indefinitely, since
  that would imply it eventually becomes larger than the entire economy.
- Margins: uses the company's own disclosed Adjusted Operating EBITDA
  margin (~30.2%, Q2 2026) minus an estimated D&A load to approximate
  a genuine EBIT margin. NOTE: an earlier version of this model used a
  flawed proxy (IncomeLossFromContinuingOperations.../revenue, ~15.3%)
  which sits AFTER interest expense -- using it as "operating margin"
  double-counted the cost of debt (once there, again via WACC) and
  implied a price of $10-38/share vs. an actual trading price of
  $130+. Caught by sanity-checking forecast FCF against FY2025 actuals.
- Terminal growth rate: 2.5%, roughly in line with long-run US GDP
  growth / inflation expectations.
"""

from __future__ import annotations
from model.wacc import compute_wacc


FORECAST_ASSUMPTIONS = {
    "fy2026_revenue": 5_600_000_000,

    "growth_fade_path": [0.18, 0.14, 0.11, 0.08, 0.06],  # FY2026-FY2030

    "gross_margin": 0.462,

    # Company-disclosed Adjusted Operating EBITDA margin (~30.2%,
    # Q2 2026 earnings release) minus an estimated D&A load (~6% of
    # revenue, matching capex_pct_revenue under the D&A~=capex
    # simplification) to approximate a genuine EBIT margin.
    "ebitda_margin": 0.302,
    "operating_margin": 0.302 - 0.060,  # ~24.2% EBIT margin estimate

    "tax_rate": 0.24,

    "capex_pct_revenue": 0.060,

    "nwc_pct_revenue_change": 0.01,

    "terminal_growth_rate": 0.025,
}


def build_revenue_forecast(assumptions: dict) -> list[dict]:
    """
    Builds year-by-year revenue forecast starting from the FY2026
    guidance anchor, applying the growth fade path for subsequent years.
    """
    forecast = []
    revenue = assumptions["fy2026_revenue"]
    fiscal_year = 2026

    for i, growth_rate in enumerate(assumptions["growth_fade_path"]):
        if i == 0:
            forecast.append({"fy": fiscal_year, "revenue": revenue, "growth_rate": growth_rate})
        else:
            revenue = revenue * (1 + growth_rate)
            forecast.append({"fy": fiscal_year, "revenue": revenue, "growth_rate": growth_rate})
        fiscal_year += 1

    return forecast


def build_unlevered_fcf_forecast(assumptions: dict) -> list[dict]:
    """
    Builds the full unlevered free cash flow forecast:
    Revenue -> Operating Income (EBIT) -> NOPAT (after-tax EBIT) ->
    + D&A add-back -> - capex -> - change in NWC -> Unlevered FCF
    """
    revenue_forecast = build_revenue_forecast(assumptions)
    fcf_forecast = []

    prior_revenue = None
    for year in revenue_forecast:
        revenue = year["revenue"]
        operating_income = revenue * assumptions["operating_margin"]
        nopat = operating_income * (1 - assumptions["tax_rate"])

        capex = revenue * assumptions["capex_pct_revenue"]

        # D&A is a non-cash expense already subtracted within operating
        # income -- it must be added back before subtracting capex, or
        # cash flow is understated by the full capex amount.
        # Simplifying assumption: D&A ~= capex for a mature industrial
        # business without a detailed PP&E schedule.
        depreciation_and_amortization = capex

        if prior_revenue is None:
            nwc_change = 0
        else:
            nwc_change = (revenue - prior_revenue) * assumptions["nwc_pct_revenue_change"]

        unlevered_fcf = nopat + depreciation_and_amortization - capex - nwc_change

        fcf_forecast.append({
            "fy": year["fy"],
            "revenue": revenue,
            "operating_income": operating_income,
            "nopat": nopat,
            "capex": capex,
            "nwc_change": nwc_change,
            "unlevered_fcf": unlevered_fcf,
        })

        prior_revenue = revenue

    return fcf_forecast


def discount_cash_flows(fcf_forecast: list[dict], wacc: float, base_year: int = 2025) -> list[dict]:
    """Discounts each year's unlevered FCF back to present value using WACC."""
    discounted = []
    for year in fcf_forecast:
        period = year["fy"] - base_year
        discount_factor = 1 / ((1 + wacc) ** period)
        pv_fcf = year["unlevered_fcf"] * discount_factor
        discounted.append({**year, "period": period, "discount_factor": discount_factor, "pv_fcf": pv_fcf})
    return discounted


def compute_terminal_value(final_year_fcf: float, wacc: float, terminal_growth: float) -> float:
    """Gordon Growth terminal value: TV = FCF_(n+1) / (WACC - g)"""
    next_year_fcf = final_year_fcf * (1 + terminal_growth)
    return next_year_fcf / (wacc - terminal_growth)


def run_dcf(assumptions: dict = FORECAST_ASSUMPTIONS, wacc_override: float = None) -> dict:
    wacc_result = compute_wacc()
    wacc = wacc_override if wacc_override is not None else wacc_result["wacc"]
    fcf_forecast = build_unlevered_fcf_forecast(assumptions)
    discounted = discount_cash_flows(fcf_forecast, wacc)

    sum_pv_fcf = sum(year["pv_fcf"] for year in discounted)

    final_year_fcf = discounted[-1]["unlevered_fcf"]
    final_period = discounted[-1]["period"]
    terminal_value = compute_terminal_value(final_year_fcf, wacc, assumptions["terminal_growth_rate"])
    pv_terminal_value = terminal_value / ((1 + wacc) ** final_period)

    enterprise_value = sum_pv_fcf + pv_terminal_value

    total_debt = wacc_result["total_debt"]
    cash = 915_000_000  # FY2025 actual, from model/statements.py pull

    equity_value = enterprise_value - total_debt + cash

    shares_outstanding = 209_000_000

    implied_price_per_share = equity_value / shares_outstanding

    return {
        "wacc": wacc,
        "discounted_fcf": discounted,
        "sum_pv_fcf": sum_pv_fcf,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value,
        "enterprise_value": enterprise_value,
        "total_debt": total_debt,
        "cash": cash,
        "equity_value": equity_value,
        "shares_outstanding": shares_outstanding,
        "implied_price_per_share": implied_price_per_share,
    }


def print_dcf_summary(result: dict) -> None:
    print("\n--- Unlevered FCF Forecast ---")
    print(f"{'FY':<6}{'Revenue':>15}{'Op Income':>15}{'NOPAT':>15}{'Capex':>12}{'FCF':>15}{'PV of FCF':>15}")
    for year in result["discounted_fcf"]:
        print(
            f"{year['fy']:<6}"
            f"{year['revenue']:>15,.0f}"
            f"{year['operating_income']:>15,.0f}"
            f"{year['nopat']:>15,.0f}"
            f"{year['capex']:>12,.0f}"
            f"{year['unlevered_fcf']:>15,.0f}"
            f"{year['pv_fcf']:>15,.0f}"
        )

    print(f"\nWACC used for discounting:        {result['wacc']:.2%}")
    print(f"Sum of PV of explicit FCFs:        ${result['sum_pv_fcf']:,.0f}")
    print(f"Terminal value (undiscounted):     ${result['terminal_value']:,.0f}")
    print(f"PV of terminal value:              ${result['pv_terminal_value']:,.0f}")
    print(f"\nImplied Enterprise Value:          ${result['enterprise_value']:,.0f}")
    print(f"(-) Total Debt:                    ${result['total_debt']:,.0f}")
    print(f"(+) Cash:                          ${result['cash']:,.0f}")
    print(f"Implied Equity Value:              ${result['equity_value']:,.0f}")
    print(f"Shares Outstanding:                {result['shares_outstanding']:,.0f}")
    print(f"\nImplied Price Per Share:           ${result['implied_price_per_share']:,.2f}")


if __name__ == "__main__":
    result = run_dcf()
    print_dcf_summary(result)
