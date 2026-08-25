"""
model/derived_metrics.py

Computes derived financial metrics that aren't directly available as
XBRL tags -- Gross Profit, margins, YoY growth rates. This is where
analytical judgment enters the pipeline: raw pulled data becomes the
kind of metrics an actual analyst would look at.

Why these specific derivations:
- gross_profit: Qnity does not tag this directly (confirmed by exploring
  all available tags -- see model/statements.py). Computed here instead.
- margins: standard analyst lens on profitability trend.
- yoy_growth: the real signal in a 3-statement model is the TREND, not
  any single year's absolute figures.
"""

from __future__ import annotations
import pandas as pd


def add_derived_metrics(annual_table: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the combined annual historical table (from
    model.statements.build_annual_table) and adds computed columns.
    Does not mutate the input table.
    """
    df = annual_table.copy()

    # --- Gross profit & margin ---
    if "revenue" in df.columns and "cost_of_revenue" in df.columns:
        df["gross_profit"] = df["revenue"] - df["cost_of_revenue"]
        df["gross_margin"] = df["gross_profit"] / df["revenue"]

    # --- Operating margin (using our documented proxy -- see
    # model/statements.py note on why this isn't a true operating
    # income line for Qnity) ---
    if "operating_income" in df.columns and "revenue" in df.columns:
        df["operating_margin"] = df["operating_income"] / df["revenue"]

    # --- Net margin ---
    if "net_income" in df.columns and "revenue" in df.columns:
        df["net_margin"] = df["net_income"] / df["revenue"]

    # --- Year-over-year growth rates ---
    for col in ["revenue", "net_income", "operating_cash_flow"]:
        if col in df.columns:
            df[f"{col}_yoy_growth"] = df[col].pct_change()

    # --- Free cash flow ---
    if "operating_cash_flow" in df.columns and "capex" in df.columns:
        df["free_cash_flow"] = df["operating_cash_flow"] - df["capex"]

    return df


def summarize_trend(df: pd.DataFrame, column: str) -> str:
    """
    Quick human-readable summary of a column's trend across years --
    useful for a first-pass sanity check before writing the thesis.
    """
    if column not in df.columns:
        return f"Column '{column}' not found."

    valid = df[["fy", column]].dropna()
    if len(valid) < 2:
        return f"Not enough data points for '{column}' to summarize a trend."

    first_year, first_val = valid.iloc[0]
    last_year, last_val = valid.iloc[-1]
    change_pct = (last_val - first_val) / abs(first_val) * 100

    direction = "increased" if change_pct > 0 else "decreased"
    is_ratio = "margin" in column or "growth" in column
    if is_ratio:
        first_str = f"{first_val:.1%}"
        last_str = f"{last_val:.1%}"
    else:
        first_str = f"{first_val:,.0f}"
        last_str = f"{last_val:,.0f}"

    return (
        f"{column}: {direction} {abs(change_pct):.1f}% from "
        f"{first_str} (FY{int(first_year)}) to "
        f"{last_str} (FY{int(last_year)})"
    )

if __name__ == "__main__":
    from data.fetch import fetch_company_facts
    from model.statements import build_annual_table

    QNITY_CIK = "2058873"
    facts = fetch_company_facts(QNITY_CIK)

    annual_table = build_annual_table(facts)
    enriched = add_derived_metrics(annual_table)

    print("\n--- Enriched Annual Table (with derived metrics) ---")
    print(enriched.to_string(index=False))

    print("\n--- Trend Summaries ---")
    for col in ["revenue", "gross_margin", "net_income", "free_cash_flow"]:
        print(summarize_trend(enriched, col))

    enriched.to_csv("data/qnity_annual_enriched.csv", index=False)
    print("\nSaved to data/qnity_annual_enriched.csv")
