"""
CLI test tool for TenderBee Tender Discovery & Multi-Criteria Search Engine.
Usage:
    .venv/bin/python scripts/test_search.py "tenders related to services in bihar"
    .venv/bin/python scripts/test_search.py "works in patna above 5 cr"
    .venv/bin/python scripts/test_search.py --state Bihar --category Services --min-val 10000000
    .venv/bin/python scripts/test_search.py "sanitation" --json
"""
import argparse
import json
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.apps.tenders.search import TenderSearchService, TenderSearchFilter, QueryParser


def main():
    parser = argparse.ArgumentParser(description="TenderBee Multi-Criteria Tender Discovery")
    parser.add_argument("prompt", nargs="?", default=None, help="Natural language query (e.g. 'services in bihar above 1 cr')")
    parser.add_argument("--state", help="Filter by Indian State (e.g. Bihar, Maharashtra)")
    parser.add_argument("--category", choices=["Services", "Works", "Goods"], help="Filter by procurement category")
    parser.add_argument("--min-val", type=float, help="Minimum estimated contract value in INR")
    parser.add_argument("--max-val", type=float, help="Maximum estimated contract value in INR")
    parser.add_argument("--tenure", type=int, help="Minimum tenure in months")
    parser.add_argument("--city", help="City or district (e.g. Patna, Gaya)")
    parser.add_argument("--buyer", help="Buyer or issuing authority")
    parser.add_argument("--json", action="store_true", help="Print raw JSON output")

    args = parser.parse_args()
    service = TenderSearchService()

    if args.prompt:
        # Natural language discovery
        result = service.search_by_prompt(args.prompt)
    else:
        # Structured parameter discovery
        filters = TenderSearchFilter(
            state=args.state,
            category=args.category,
            city_or_district=args.city,
            min_value_inr=args.min_val,
            max_value_inr=args.max_val,
            min_tenure_months=args.tenure,
            buyer_name=args.buyer,
        )
        result = service.search(filters)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return

    # Formatted CLI presentation
    print("=" * 80)
    print("TENDERBEE TENDER DISCOVERY ENGINE")
    if args.prompt:
        print(f"Query Prompt  : \"{args.prompt}\"")
    print(f"Filters       : {json.dumps(result['applied_filters'])}")
    print(f"Total Matches : {result['total_matches']}")
    print("=" * 80)

    if not result["results"]:
        print("\n❌ No matching tenders found for the specified criteria.")
        print("💡 Try broadening your search or adjusting value/tenure thresholds.\n")
        return

    for idx, t in enumerate(result["results"], 1):
        val_str = f"₹{t['estimated_value_inr']:,.2f}" if t.get("estimated_value_inr") else "Not Specified"
        emd_str = f"₹{t['emd_amount_inr']:,.2f}" if t.get("emd_amount_inr") else "Exempted / Nil"
        tenure_str = f"{t['tenure_months']} Months" if t.get("tenure_months") else "Standard"

        print(f"\n[{idx}] {t['title']}")
        print(f"    Tender ID : {t['tender_number']} | Portal: {t['portal']}")
        print(f"    Buyer     : {t['buyer_name']}")
        print(f"    Location  : {t['state']} | Category: {t['category']}")
        print(f"    Financials: Estimated Value: {val_str} | EMD: {emd_str}")
        print(f"    Tenure    : {tenure_str} | Deadline: {t['submission_deadline']}")
        print(f"    👉 Deep Intake Command:")
        print(f"       .venv/bin/python scripts/test_intake.py \"{t['tender_number']}\"")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
