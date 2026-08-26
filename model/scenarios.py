"""
model/scenarios.py

Runs the DCF engine (model/dcf.py) across three distinct assumption
sets -- Bear, Base, Bull -- to produce a defensible valuation RANGE
rather than a single point estimate. This is standard equity research
practice: a single DCF output invites the (correct) criticism "what if
your assumptions are wrong?" A scenario range answers that question
directly by showing how sensitive the valuation is to the two
assumptions that matter most here -- growth and margin -- while holding
WACC and terminal growth constant across all three (changing those too
would conflate "different view on the business" with "different view on
risk/discount rate," which are separate questions).

Each scenario's assumptions are tied to something specific and real,
not just arbitrarily higher/lower numbers -- see inline notes.
"""

from __future__ import annotations
from model.dcf import FORECAST_ASSUMPTIONS, run_dcf


def _build_scenario(base: dict, overrides: dict) -> dict:
    """Copies the base assumption set and applies scenario-specific overrides."""
    scenario = dict(base)
    scenario.update(overrides)
    return scenario


# --- BASE CASE ---
# This is exactly what we built and ran last session: FY2026 revenue
# anchored to management's actual guidance midpoint ($5.6B), growth
# fading from ~18% toward a 6% terminal-adjacent rate, EBITDA margin
# held flat at the company's own disclosed 30.2% (Q2 2026).
BASE_CASE = dict(FORECAST_ASSUMPTIONS)


# --- BULL CASE ---
# Rationale, tied to real, specific evidence rather than optimism for
# its own sake:
# - Growth fades more slowly: justified by 9 consecutive quarters of
#   profitable growth and TWO guidance raises within 2026 alone --
#   a real, observed pattern of underestimating this company, not
#   just a hopeful assumption.
# - EBITDA margin expands from 30.2% to 33%: justified by the
#   transformation plan management explicitly cited as targeting
#   "operational efficiencies and cost savings over the next two
#   years" (Q2 2026 earnings), plus the gross margin expansion trend
#   already observed in the historical data (43.5% -> 46.2%, FY23-25).
BULL_CASE = _build_scenario(BASE_CASE, {
    "growth_fade_path": [0.18, 0.16, 0.14, 0.11, 0.09],
    "ebitda_margin": 0.33,
    "operating_margin": 0.33 - 0.060,
})


# --- BEAR CASE ---
# Rationale, tied to real, specific risks disclosed in the 10-K rather
# than generic pessimism:
# - Growth fades faster/lower: reflects the customer concentration risk
#   (top 10 customers = 34% of FY2025 net sales, Samsung alone 11%) and
#   geographic concentration (~33% of FY2025 sales from China) -- a
#   single customer loss or export-control shock could compress growth
#   well below the base case quickly.
# - EBITDA margin compresses to 27%: reflects the semiconductor industry's
#   disclosed cyclicality (Qnity itself states the industry "has
#   historically been, and is likely to continue to be, cyclical") --
#   a cyclical downturn typically hits margins before it hits revenue,
#   as fixed costs don't flex down as fast as volume.
BEAR_CASE = _build_scenario(BASE_CASE, {
    "growth_fade_path": [0.18, 0.10, 0.06, 0.04, 0.03],
    "ebitda_margin": 0.27,
    "operating_margin": 0.27 - 0.060,
})


SCENARIOS = {
    "Bear": BEAR_CASE,
    "Base": BASE_CASE,
    "Bull": BULL_CASE,
}


def run_all_scenarios() -> dict:
    """Runs the DCF engine once per scenario, returns all results keyed by name."""
    results = {}
    for name, assumptions in SCENARIOS.items():
        results[name] = run_dcf(assumptions)
    return results


def print_scenario_comparison(results: dict) -> None:
    print("\n--- Scenario Comparison: Implied Valuation Range ---\n")
    print(f"{'Scenario':<10}{'FY2030 Revenue':>18}{'EBITDA Margin':>16}{'Enterprise Value':>20}{'Implied Price':>16}")
    for name in ["Bear", "Base", "Bull"]:
        r = results[name]
        final_year_revenue = r["discounted_fcf"][-1]["revenue"]
        ebitda_margin = SCENARIOS[name]["ebitda_margin"]
        print(
            f"{name:<10}"
            f"{final_year_revenue:>18,.0f}"
            f"{ebitda_margin:>16.1%}"
            f"{r['enterprise_value']:>20,.0f}"
            f"${r['implied_price_per_share']:>14,.2f}"
        )

    print("\nAll scenarios use the SAME WACC and terminal growth rate --")
    print("only growth path and margin assumptions vary between them.")
    print("This isolates 'view on the business' from 'view on risk/discount rate.'")


if __name__ == "__main__":
    results = run_all_scenarios()
    print_scenario_comparison(results)
