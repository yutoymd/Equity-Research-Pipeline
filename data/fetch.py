"""
data/fetch.py

Pulls raw XBRL financial facts for a company from SEC EDGAR's free
companyfacts API and returns them as a clean pandas DataFrame.

Why SEC EDGAR directly, instead of yfinance/similar libraries?
- It's the primary source: these are the exact numbers companies filed,
  not a third party's re-scraped/re-labeled version.
- yfinance and similar free tools are known to have line-item mislabeling,
  missing restatements, and inconsistent coverage. Going to the primary
  source and reconciling against it later is what makes this pipeline
  defensible in an interview.

Docs: https://www.sec.gov/edgar/sec-api-documentation
"""

import time
import requests
import pandas as pd

# SEC REQUIRES a descriptive User-Agent identifying you. Requests without
# one (or with a generic one) get blocked. Put your real name/email here --
# this is standard API etiquette, not just an SEC quirk.
HEADERS = {
    "User-Agent": "Yuto Yamada yutoyamada81@gmail.com"
}

BASE_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


def format_cik(cik: str | int) -> str:
    """SEC wants CIKs as 10-digit, zero-padded strings."""
    return str(cik).zfill(10)


def fetch_company_facts(cik: str | int) -> dict:
    """
    Hits the companyfacts endpoint for a single company and returns the
    raw JSON. This JSON contains EVERY XBRL fact the company has ever
    tagged in a filing -- revenue, assets, liabilities, shares outstanding,
    hundreds of line items, going back years.
    """
    url = BASE_URL.format(cik=format_cik(cik))
    response = requests.get(url, headers=HEADERS, timeout=15)

    # SEC rate-limits aggressively. A 403 usually means either a missing/bad
    # User-Agent, or you're requesting too fast. Fail loud, not silent --
    # a silently empty dataframe later is much harder to debug than a
    # clear error now.
    if response.status_code != 200:
        raise RuntimeError(
            f"SEC EDGAR request failed [{response.status_code}] for CIK {cik}. "
            f"Check your User-Agent header and request rate."
        )

    return response.json()


def extract_fact_series(company_facts: dict, tag: str, taxonomy: str = "us-gaap") -> pd.DataFrame:
    """
    Pull a single line item (e.g. 'Revenues', 'Assets', 'NetIncomeLoss')
    out of the raw companyfacts JSON into a tidy DataFrame.

    XBRL tags are standardized names companies use when they file --
    'us-gaap:Revenues', 'us-gaap:Assets', etc. You'll need to explore the
    raw JSON to find the exact tag names Qnity used, since not every
    company tags things identically (this is one of the "data quality"
    gotchas -- worth noting in your README once you hit it).
    """
    try:
        raw = company_facts["facts"][taxonomy][tag]["units"]
    except KeyError:
        raise KeyError(
            f"Tag '{taxonomy}:{tag}' not found for this company. "
            f"Run explore_available_tags() to see what's actually available."
        )

    # Facts are usually reported in USD, but check units defensively.
    unit_key = "USD" if "USD" in raw else list(raw.keys())[0]
    records = raw[unit_key]

    df = pd.DataFrame(records)
    df["tag"] = tag

    # Keep only annual (10-K, "FY") and quarterly (10-Q, "Q1"/"Q2"/"Q3")
    # filings -- the API also returns some duplicate/amended entries you
    # generally want to filter later once you see them.
    return df


def explore_available_tags(company_facts: dict, taxonomy: str = "us-gaap") -> list[str]:
    """
    Utility for your first exploration session: lists every tag available
    for this company under a given taxonomy, so you can find the exact
    names for Revenue, COGS, Assets, Liabilities, etc.
    """
    return sorted(company_facts["facts"][taxonomy].keys())


if __name__ == "__main__":
    # --- Qnity Electronics, Inc. ---
    QNITY_CIK = "2058873"

    print(f"Fetching company facts for CIK {QNITY_CIK} ...")
    facts = fetch_company_facts(QNITY_CIK)

    entity_name = facts.get("entityName", "UNKNOWN")
    print(f"Retrieved data for: {entity_name}")

    tags = explore_available_tags(facts)
    print(f"\n{len(tags)} available us-gaap tags. First 20:")
    for t in tags[:20]:
        print(f"  - {t}")

    print("\nTry extract_fact_series(facts, 'Revenues') next, or search the")
    print("tags list above for 'Revenue', 'Assets', 'Liabilities', etc.")
