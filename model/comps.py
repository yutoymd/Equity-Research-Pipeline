"""
model/comps.py

Cross-checks the DCF valuation (model/dcf.py, model/scenarios.py)
against a comparable-companies EV/EBITDA approach. This exists because
a DCF alone invites a fair challenge: "how does this compare to how the
market actually prices similar businesses?" If the DCF and comps
approach land in similar places, that's real confidence. If they
diverge sharply (as we'll see they do here), that divergence itself is
the analytical finding worth explaining.

COMP SET AND MULTIPLES -- sourced, dated:
Source: TIKR.com, NTM EV/EBITDA multiples as of ~May 2026 (MKS Q1 2026
earnings commentary article). This is a real, current comp set spanning
the semiconductor equipment/materials space -- not idealized peers.

NOTE ON COMP SELECTION: none of these companies are perfectly identical
to Qnity (a materials/consumables supplier, not an equipment maker like
LRCX/KLAC/AMAT/MKSI), but they represent the closest publicly-traded
peer group in the semiconductor supply chain. Entegris (ENTG) is the
closest direct comp -- also a materials/process solutions supplier, not
an equipment maker -- and is weighted accordingly in the analysis below.
"""

from __future__ import annotations


COMPS = [
    {"name": "Lam Research (LRCX)", "ev_ebitda_ntm": 31.14, "type": "Equipment"},
    {"name": "KLA Corporation (KLAC)", "ev_ebitda_ntm": 30.36, "type": "Equipment"},
    {"name": "Applied Materials (AMAT)", "ev_ebitda_ntm": 23.44, "type": "Equipment"},
    {"name": "Entegris (ENTG)", "ev_ebitda_ntm": 21.90, "type": "Materials (closest direct comp)"},
    {"name": "MKS Instruments (MKSI)", "ev_ebitda_ntm": 17.42, "type": "Equipment/Materials"},
]


def comps_summary_stats(comps: list[dict]) -> dict:
    multiples = [c["ev_ebitda_ntm"] for c in comps]
    return {
        "min": min(multiples),
        "max": max(multiples),
        "median": sorted(multiples)[len(multiples) // 2],
        "mean": sum(multiples) / len(multiples),
        "entegris_only": next(c["ev_ebitda_ntm"] for c in comps if "ENTG" in c["name"]),
    }


def comps_implied_valuation(
    fy2026_ebitda: float,
    total_debt: float,
    cash: float,
    shares_outstanding: float,
    comps: list[dict] = COMPS,
) -> dict:
    """
    Applies each comp's multiple (and summary stats) to Qnity's own
    forward EBITDA to derive an implied Enterprise Value, Equity Value,
    and price per share under each.
    """
    stats = comps_summary_stats(comps)
    results = {}

    for label, multiple in [
        ("Low (min comp)", stats["min"]),
        ("Entegris only (closest direct comp)", stats["entegris_only"]),
        ("Median comp", stats["median"]),
        ("Mean comp", stats["mean"]),
        ("High (max comp)", stats["max"]),
    ]:
        implied_ev = fy2026_ebitda * multiple
        implied_equity_value = implied_ev - total_debt + cash
        implied_price = implied_equity_value / shares_outstanding

        results[label] = {
            "multiple": multiple,
            "implied_ev": implied_ev,
            "implied_equity_value": implied_equity_value,
            "implied_price": implied_price,
        }

    return results


def print_comps_analysis(results: dict, dcf_base_price: float) -> None:
    print("\n--- Comps-Based Valuation (EV/EBITDA Cross-Check) ---\n")
    print(f"{'Basis':<38}{'Multiple':>10}{'Implied EV':>18}{'Implied Price':>16}")
    for label, r in results.items():
        print(
            f"{label:<38}"
            f"{r['multiple']:>9.1f}x"
            f"{r['implied_ev']:>18,.0f}"
            f"${r['implied_price']:>14,.2f}"
        )

    print(f"\nFor comparison -- our DCF Base Case implied price: ${dcf_base_price:,.2f}")
    print(
        "\nIf comps-implied prices sit well ABOVE the DCF range, this "
        "supports the hypothesis that the market is pricing Qnity using "
        "a peer-multiple framework rather than (or in addition to) "
        "fundamental cash-flow generation -- a real, defensible reason "
        "for the DCF/market price gap, not necessarily a flaw in either method."
    )


if __name__ == "__main__":
    from model.dcf import run_dcf

    fy2026_ebitda = 5_600_000_000 * 0.302

    dcf_result = run_dcf()

    comps_results = comps_implied_valuation(
        fy2026_ebitda=fy2026_ebitda,
        total_debt=dcf_result["total_debt"],
        cash=dcf_result["cash"],
        shares_outstanding=dcf_result["shares_outstanding"],
    )

    print_comps_analysis(comps_results, dcf_result["implied_price_per_share"])
