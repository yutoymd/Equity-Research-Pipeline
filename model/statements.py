
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
        # Qnity's XBRL data does not tag Gross Profit as a standalone
        # line item. Compute later as revenue - cost_of_revenue.
    ],
    "operating_income": [
        # Qnity does not tag a true Operating Income line. Closest proxy
        # is IncomeLossFromContinuingOperations..., which sits AFTER
        # nonoperating items -- NOT equivalent to real operating income.
        "IncomeLossFromContinuingOperationsIncludingPortionAttributableToNoncontrollingInterest",
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
	"PaymentsToAcquireProductiveAssets",
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
    Filters to full-year (annual) data. Handles two different XBRL fact
    shapes:
    - "duration" facts (Revenue, NetIncomeLoss, capex, etc.) span a
      period and have both 'start' and 'end' dates -- annual ones are
      identified by spanning ~365 days.
    - "instant" facts (Assets, Liabilities, Cash, etc.) are a snapshot
      at a single point in time and only have an 'end' date -- these are
      identified by keeping only 10-K-sourced values (annual report
      balance sheet date), since there's no "duration" to check.

    Rather than trusting the 'fp' label alone, which can be missing/None
    for facts sourced from filings like DEF 14A rather than the 10-K.
    """
    df = df.copy()
    df["end"] = pd.to_datetime(df["end"])

    if "start" in df.columns and df["start"].notna().any():
        # Duration fact.
        df["start"] = pd.to_datetime(df["start"])
        df["period_days"] = (df["end"] - df["start"]).dt.days
        annual = df[(df["period_days"] >= 350) & (df["period_days"] <= 380)].copy()
    else:
        # Instant fact -- no duration to check. Restrict to values
        # reported in the annual 10-K itself to avoid quarterly
        # snapshots.
        annual = df[df["form"] == "10-K"].copy()

    annual["fy"] = annual["end"].dt.year
    annual = annual.sort_values("fy").drop_duplicates(subset=["fy"], keep="last")
    return annual[["fy", "val", "form", "filed"]]

def build_annual_table(company_facts: dict) -> pd.DataFrame:
    """
    Pulls every line item in TAG_CANDIDATES, filters each to annual (FY)
    data only, and merges them into a single wide table: one row per
    fiscal year, one column per line item. This is the actual starting
    point for 3-statement linking -- a clean, combined historical view
    instead of one line item at a time.
    """
    statements = build_core_statement_table(company_facts)

    combined = None
    for line_item, df in statements.items():
        if df is None:
            continue  # skip line items with no matching tag (e.g. gross_profit)

        annual = annual_only(df)[["fy", "val"]].rename(columns={"val": line_item})

        if combined is None:
            combined = annual
        else:
            combined = combined.merge(annual, on="fy", how="outer")

    return combined.sort_values("fy").reset_index(drop=True)

if __name__ == "__main__":
    from data.fetch import fetch_company_facts

    QNITY_CIK = "2058873"
    facts = fetch_company_facts(QNITY_CIK)

    annual_table = build_annual_table(facts)

    print("\n--- Combined Annual Historical Table ---")
    print(annual_table.to_string(index=False))

    annual_table.to_csv("data/qnity_annual_historicals.csv", index=False)
    print("\nSaved to data/qnity_annual_historicals.csv")
