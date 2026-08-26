"""
model/sensitivity.py

Builds a two-way sensitivity table: implied share price across a grid
of WACC and terminal growth rate assumptions, holding the Base Case
revenue/margin forecast constant. This is a standard, expected
component of a real DCF -- a single-point valuation invites the fair
challenge "how sensitive is this to your two most subjective inputs?"
This table answers that directly.

WACC and terminal growth are the two assumptions chosen deliberately:
- WACC is sensitive to beta and equity risk premium, both of which are
  the "softest" inputs in this entire model (see model/wacc.py notes --
  beta is a comparable-company proxy, ERP is a market convention, not a
  live-sourced number).
- Terminal growth rate drives a disproportionate share of total
  Enterprise Value in any DCF (the "hockey stick" problem: most of a
  DCF's value typically comes from the terminal value, not the explicit
  forecast period), so its sensitivity deserves explicit visibility
  rather than being buried as a single assumed constant.
"""

from __future__ import annotations
from model.dcf import FORECAST_ASSUMPTIONS, run_dcf


def build_sensitivity_grid(
    wacc_range: list[float],
    terminal_growth_range: list[float],
    base_assumptions: dict = FORECAST_ASSUMPTIONS,
) -> dict:
    """
    Returns a nested dict: {wacc: {terminal_growth: implied_price}}
    """
    grid = {}
    for wacc in wacc_range:
        grid[wacc] = {}
        for tg in terminal_growth_range:
            # Guard against WACC <= terminal growth, which makes the
            # Gordon Growth denominator zero or negative -- mathematically
            # invalid (implies infinite or negative terminal value).
            if wacc <= tg:
                grid[wacc][tg] = None
                continue

            assumptions = dict(base_assumptions)
            assumptions["terminal_growth_rate"] = tg

            result = run_dcf(assumptions, wacc_override=wacc)
            grid[wacc][tg] = result["implied_price_per_share"]

    return grid


def print_sensitivity_table(
    grid: dict,
    wacc_range: list[float],
    terminal_growth_range: list[float],
    base_wacc: float,
    base_tg: float,
) -> None:
    print("\n--- Sensitivity Table: Implied Price Per Share ---")
    print("(rows = WACC, columns = Terminal Growth Rate)\n")

    # Header row
    header = "WACC \\ TG".ljust(12)
    for tg in terminal_growth_range:
        header += f"{tg:>10.1%}"
    print(header)

    for wacc in wacc_range:
        row = f"{wacc:>10.2%}  "
        for tg in terminal_growth_range:
            price = grid[wacc][tg]
            if price is None:
                row += f"{'  n/a':>10}"
            else:
                row += f"{price:>10.2f}"
        # Flag the base case row/intersection for readability
        marker = "  <- base WACC" if abs(wacc - base_wacc) < 1e-9 else ""
        print(row + marker)

    print(
        f"\nBase case: WACC={base_wacc:.2%}, Terminal Growth={base_tg:.1%} "
        f"-> ${grid[base_wacc][base_tg]:.2f}/share"
    )
    print(
        "\nNote: 'n/a' cells occur where WACC <= Terminal Growth -- the "
        "Gordon Growth formula (TV = FCF / (WACC - g)) is mathematically "
        "invalid there (implies a business growing faster than its own "
        "discount rate forever, i.e. infinite value)."
    )


if __name__ == "__main__":
    from model.wacc import compute_wacc

    raw_wacc = compute_wacc()["wacc"]
    base_wacc = round(raw_wacc, 4)  # round FIRST, so this matches a grid key exactly
    base_tg = round(FORECAST_ASSUMPTIONS["terminal_growth_rate"], 4)

    # +/- 1.5 points around the base WACC, in 0.5-point steps
    wacc_range = [round(base_wacc + step, 4) for step in [-0.015, -0.0075, 0, 0.0075, 0.015]]

    # +/- 1.0 point around the base terminal growth, in 0.5-point steps
    tg_range = [round(base_tg + step, 4) for step in [-0.01, -0.005, 0, 0.005, 0.01]]

    grid = build_sensitivity_grid(wacc_range, tg_range)
    print_sensitivity_table(grid, wacc_range, tg_range, base_wacc, base_tg)
