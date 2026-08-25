from __future__ import annotations
"""
model/statements.py

Takes raw XBRL facts (from data/fetch.py) and assembles them into a
clean, tidy historical financial statement table.

Key design problem this solves: XBRL tag names aren't perfectly
standardized across filers. Two companies reporting "Revenue" might use
different us-gaap tags depending on when they adopted ASC 606 and how
their accountants tagged the filing. Rather than hardcoding one tag name
and failing silently, we try a list of known common variants in order
and use the first one that exists.
"""

import pandas as pd
from data.fetch import extract_fact_series


# Each line item maps to a list of candidate XBRL tags, in priority order.
# This list is a starting point based on common post-ASC-606 filer
# conventions -- you WILL need to verify these against the actual tags
# Qnity used by running explore_available_tags() first, and adjust this
# mapping. That verification step is part of the work, not a shortcut
# to skip.
TAG_CANDIDATES = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax",
        "Revenues",
    ],
    "cost_of_revenue": [
        "CostOfGoodsAndServicesSold",
        "CostOfRevenue",
        "CostOfGoodsSold",
    ],
    "gross_profit": [
        "GrossProfit",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
    ],
    "net_income": [
        "NetIncomeLoss",
    ],
    "total_assets": [
        "Assets",
    ],
    "total_liabilities": [
        "Liabilities",
    ],
    "stockholders_equity": [
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ],
    "cash_and_equivalents": [
        "CashAndCashEquivalentsAtCarryingValue",
    ],
    "long_term_debt": [
        "LongTermDebtNoncurrent",
        "LongTermDebt",
    ],
    "operating_cash_flow": [
        "NetCashProvidedByUsedInOperatingActivities",
    ],
    "capex": [
        "PaymentsToAcquirePropertyPlantAndEquipment",
    ],
}


def try_extract(company_facts: dict, candidates: list[str]) -> pd.DataFrame | None:
    """Try each candidate tag in order; return the first one that exists."""
    for tag in candidates:
        try:
            return extract_fact_series(company_facts, tag)
        except KeyError:
            continue
    return None


def build_core_statement_table(company_facts: dict) -> dict[str, pd.DataFrame]:
    """
    Pull every line item in TAG_CANDIDATES and return a dict of
    {line_item_name: DataFrame}. Line items that couldn't be found under
    any candidate tag come back as None -- check for these explicitly,
    don't let them disappear silently.
    """
    results = {}
    missing = []

    for line_item, candidates in TAG_CANDIDATES.items():
        df = try_extract(company_facts, candidates)
        if df is None:
            missing.append(line_item)
        results[line_item] = df

    if missing:
        print(f"WARNING: could not find tags for: {missing}")
        print("Run explore_available_tags() and update TAG_CANDIDATES for these.")

    return results


def annual_only(df: pd.DataFrame) -> pd.DataFrame:
    """
    The companyfacts API returns quarterly (10-Q, fp='Q1'/'Q2'/'Q3') and
    annual (10-K, fp='FY') data mixed together, plus sometimes duplicate
    entries from amended filings. This filters down to annual (fp=='FY')
    rows only, sorted by fiscal year -- your starting point for a clean
    3-year historical table.

    NOTE: inspect the raw 'form' and 'fp' columns yourself before trusting
    this blindly -- duplicate/restated entries are exactly the kind of
    silent data-quality issue flagged in the README's reconciliation
    section.
    """
    annual = df[df["fp"] == "FY"].copy()
    annual = annual.sort_values("fy").drop_duplicates(subset=["fy"], keep="last")
    return annual[["fy", "val", "form", "filed"]]


if __name__ == "__main__":
    from data.fetch import fetch_company_facts

    QNITY_CIK = "2058873"
    facts = fetch_company_facts(QNITY_CIK)

    statements = build_core_statement_table(facts)

    print("\n--- Revenue (annual) ---")
    if statements["revenue"] is not None:
        print(annual_only(statements["revenue"]))
    else:
        print("Not found under any candidate tag -- inspect available tags manually.")
