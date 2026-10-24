"""
Interactive CLI for TenderBee Tender Discovery & Multi-Criteria Search Engine.
Search for tenders using natural language or multi-dimensional filters, then
choose between a fast Skimmed View or deep Detailed PDF Extraction View.

Usage:
    .venv/bin/python scripts/test_search.py
    .venv/bin/python scripts/test_search.py "services in haryana"
    .venv/bin/python scripts/test_search.py "railway tenders above 10 cr"
    .venv/bin/python scripts/test_search.py --tender "BIH/EPROC2/140751" --mode detailed
    .venv/bin/python scripts/test_search.py --state Bihar --category Services
    .venv/bin/python scripts/test_search.py "patna" --json
"""
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure project root is in sys.path
REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.apps.tenders.search import TenderSearchService, TenderSearchFilter, QueryParser


def print_divider(char="=", width=80):
    print(char * width)


def display_skimmed_view(tender: Dict[str, Any]):
    print_divider("=")
    print(f"TENDERBEE VIEW MODE: SKIMMED")
    print(f"Tender Number: {tender.get('tender_number')}  (ID: {tender.get('tender_id')})")
    print_divider("=")
    print(f"Title       : {tender.get('title')}")
    print(f"Buyer       : {tender.get('buyer_name')}")
    print(f"Location    : {tender.get('state', 'All India')} | Category: {tender.get('category', 'Services')}")
    
    val = tender.get("estimated_value_inr") or 0
    emd = tender.get("emd_amount_inr") or 0
    val_str = f"₹{val:,.2f}" if val else "Not Specified"
    emd_str = f"₹{emd:,.2f}" if emd else "Exempted / Nil"
    
    print(f"Value       : {val_str}")
    print(f"EMD         : {emd_str}")
    print(f"Tenure      : {tender.get('tenure_months', 'Standard')} Months" if tender.get('tenure_months') else "Tenure      : Standard Duration")
    print(f"Deadline    : {tender.get('submission_deadline')}")
    print(f"Portal      : {tender.get('portal', 'Government Portal')}")
    print(f"Source URL  : {tender.get('source_url', 'N/A')}")
    print(f"Status      : {tender.get('status', 'ACTIVE')}")
    pdf_status = "Available" if tender.get("has_pdf_document") else "Pending Upload / Intake"
    print(f"PDF Document: {pdf_status}")
    print_divider("=")


def display_json_view(tender: Dict[str, Any]):
    print_divider("=")
    print(f"TENDERBEE VIEW MODE: RAW STRUCTURED JSON PAYLOAD")
    print(f"Tender Number: {tender.get('tender_number')}  (ID: {tender.get('tender_id')})")
    if tender.get("extracted_json_path"):
        print(f"Snapshot File: {tender.get('extracted_json_path')}")
    print_divider("=")
    print(json.dumps(tender, indent=2, default=str))
    print_divider("=")


def display_detailed_view(tender: Dict[str, Any]):
    print_divider("=")
    print(f"TENDERBEE VIEW MODE: DETAILED (DEEP PDF CLAUSE EXTRACTION)")
    print(f"Tender Number: {tender.get('tender_number')}  (ID: {tender.get('tender_id')})")
    print_divider("=")
    print(f"Title       : {tender.get('title')}")
    print(f"Buyer       : {tender.get('buyer_name')}")
    print(f"Location    : {tender.get('state', 'All India')} | Category: {tender.get('category', 'Services')}")
    
    val = tender.get("estimated_value_inr") or 0
    emd = tender.get("emd_amount_inr") or 0
    val_str = f"₹{val:,.2f}" if val else "Not Specified"
    emd_str = f"₹{emd:,.2f}" if emd else "Exempted / Nil"
    print(f"Value       : {val_str}")
    print(f"EMD         : {emd_str}")
    print(f"Deadline    : {tender.get('submission_deadline')}")
    print(f"Portal      : {tender.get('portal', 'Government Portal')}")

    pdf_status = tender.get("pdf_status", "PENDING_INTAKE")
    print(f"\n--- PDF DOCUMENT ANALYSIS ---")
    print(f"Status      : {pdf_status}")
    if tender.get("extracted_json_path"):
        print(f"Snapshot File: {tender.get('extracted_json_path')}")

    ext = tender.get("extraction")
    if ext:
        total_pages = ext.get("total_pages", "N/A")
        cov = ext.get("digital_text_coverage") or 0
        print(f"Total Pages : {total_pages}")
        print(f"Coverage    : {cov * 100:.1f}% digital text extraction")

        # Verbatim clauses
        clauses = ext.get("verbatim_clauses", [])
        print(f"\n--- VERBATIM CLAUSES EXTRACTED ({len(clauses)} clauses with 1-indexed citations) ---")
        for i, c in enumerate(clauses[:6], 1):
            page = c.get("page", "?")
            c_type = c.get("clause_type", "clause")
            quote = c.get("quote", "")
            print(f"  {i}. [Page {page}] {c_type}:")
            print(f"     \"{quote}\"")
        if len(clauses) > 6:
            print(f"  ... and {len(clauses) - 6} more verbatim clauses in full JSON schema.")

        # Eligibility rules
        elig = ext.get("eligibility_rules", {})
        if elig:
            print(f"\n--- EXTRACTED NUMERICAL ELIGIBILITY CRITERIA ---")
            if elig.get("min_annual_turnover_inr"):
                years = elig.get("turnover_years", 3)
                print(f"  • Min Annual Turnover : ₹{elig['min_annual_turnover_inr']:,.2f} (over {years} financial years)")
            if elig.get("min_liquidity_inr"):
                print(f"  • Min Liquidity/Bank  : ₹{elig['min_liquidity_inr']:,.2f}")
            if elig.get("min_work_experience_inr"):
                print(f"  • Single Work Contract: ₹{elig['min_work_experience_inr']:,.2f}")
            if "udin_mandatory" in elig:
                print(f"  • UDIN Mandatory on CA: {'Yes (Verified)' if elig['udin_mandatory'] else 'No'}")
            if "mse_exemption_allowed" in ext:
                print(f"  • MSE/MSME Exemption  : {'Allowed' if ext['mse_exemption_allowed'] else 'Not Allowed'}")

        # Mandatory documents
        docs = ext.get("mandatory_documents", [])
        if docs:
            print(f"\n--- MANDATORY DOCUMENT CHECKLIST ({len(docs)} documents) ---")
            for idx, d in enumerate(docs, 1):
                print(f"  [{idx}] {d}")
    else:
        print(f"Note: {tender.get('message', 'No PDF attached for this tender yet. Provide PDF path to extract full clauses.')}")

    # Rule Pack
    if "rule_pack" in tender and tender["rule_pack"]:
        rp = tender["rule_pack"]
        content_hash = rp.get("content_hash", "")[:16]
        rules = rp.get("rules", [])
        status = rp.get('status', 'DRAFT')
        if hasattr(status, 'value'):
            status = status.value
        elif isinstance(status, str) and '.' in status:
            status = status.split('.')[-1]
        print(f"\n--- EXECUTABLE COMPLIANCE RULE PACK ---")
        print(f"Rule Pack ID: {content_hash} | Status: {status} | Version: {rp.get('version', 1)}")
        print(f"Draft Rules : {len(rules)} executable compliance checks drafted")
        for i, r in enumerate(rules[:8], 1):
            r_type = r.get("rule_type") or r.get("type", "PASS_FAIL")
            if hasattr(r_type, "value"):
                r_type = r_type.value
            elif isinstance(r_type, str) and "." in r_type:
                r_type = r_type.split(".")[-1]
            r_id = r.get("rule_id", f"rule_{i}")
            desc = r.get("description")
            params = r.get("params") or {}
            if not desc:
                if params.get("threshold_inr") is not None:
                    desc = f"{params.get('field', 'Threshold')} {params.get('operator', '>=')} ₹{params['threshold_inr']:,.2f}"
                elif params.get("document_type") or r.get("document_type"):
                    doc_t = params.get("document_type") or r.get("document_type")
                    if hasattr(doc_t, "value"):
                        doc_t = doc_t.value
                    elif isinstance(doc_t, str) and "." in doc_t:
                        doc_t = doc_t.split(".")[-1]
                    desc = f"Mandatory Document: {doc_t}"
                elif r.get("operator") and r.get("value") is not None:
                    desc = f"{r.get('field', 'Value')} {r.get('operator')} {r.get('value')}"
                elif params.get("field"):
                    desc = f"Verify {params['field']}"
                else:
                    desc = r.get("field", r_id)

            source = r.get("source") or {}
            page_info = f" [Page {source.get('page')}]" if source.get("page") else ""
            print(f"  {i}. [{r_type.upper()}] {r_id}: {desc}{page_info}")
        if len(rules) > 8:
            print(f"  ... and {len(rules) - 8} more rules.")

    print_divider("=")


def display_search_results(results: List[Dict[str, Any]], query_info: str = ""):
    print_divider("=")
    print("TENDERBEE TENDER DISCOVERY ENGINE")
    if query_info:
        print(f"Query: {query_info}")
    print(f"Total Matches: {len(results)}")
    print_divider("=")

    if not results:
        print("\n❌ No matching tenders found for the specified criteria.")
        print("💡 Try broadening your search or adjusting thresholds.\n")
        return

    for idx, t in enumerate(results, 1):
        val = t.get("estimated_value_inr") or 0
        emd = t.get("emd_amount_inr") or 0
        val_str = f"₹{val:,.2f}" if val else "Not Specified"
        emd_str = f"₹{emd:,.2f}" if emd else "Exempted / Nil"
        tenure_str = f"{t['tenure_months']} Months" if t.get("tenure_months") else "Standard"

        print(f"\n[{idx}] {t['title']}")
        print(f"    Tender ID : {t['tender_number']} | Portal: {t.get('portal', 'Government Portal')}")
        print(f"    Buyer     : {t.get('buyer_name')}")
        print(f"    Location  : {t.get('state', 'All India')} | Category: {t.get('category', 'Services')}")
        print(f"    Financials: Value: {val_str} | EMD: {emd_str}")
        print(f"    Tenure    : {tenure_str} | Deadline: {t.get('submission_deadline')}")

    print_divider("=")


def interactive_tender_inspection(service: TenderSearchService, tender_ident: str, default_mode: str = "skim"):
    current_mode = default_mode
    while True:
        fetch_mode = "detailed" if current_mode in ("detailed", "json") else "skim"
        tender = service.get_tender(tender_ident, mode=fetch_mode)
        if not tender:
            print(f"\n❌ Tender '{tender_ident}' not found.")
            return

        if current_mode == "detailed":
            display_detailed_view(tender)
        elif current_mode == "json":
            display_json_view(tender)
        else:
            display_skimmed_view(tender)

        # Action choices
        if current_mode == "skim":
            prompt_str = (
                "\nActions: [d] Detailed View (parse PDF clauses) | [j] View JSON | [b] Back to results | [q] Quit\n"
                "Select action [d/j/b/q]: "
            )
        elif current_mode == "detailed":
            prompt_str = (
                "\nActions: [s] Skimmed View | [j] View JSON | [b] Back to results | [q] Quit\n"
                "Select action [s/j/b/q]: "
            )
        else:
            prompt_str = (
                "\nActions: [s] Skimmed View | [d] Detailed View | [j] View JSON again | [b] Back to results | [q] Quit\n"
                "Select action [s/d/j/b/q]: "
            )

        try:
            choice = input(prompt_str).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting TenderBee. Goodbye!")
            sys.exit(0)

        if choice in ("d", "detailed", "2"):
            current_mode = "detailed"
        elif choice in ("s", "skim", "1"):
            current_mode = "skim"
        elif choice in ("j", "json", "3"):
            current_mode = "json"
        elif choice in ("b", "back", "r"):
            return
        elif choice in ("q", "quit", "exit"):
            print("\nExiting TenderBee. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please select an available action.")


def interactive_search_loop(service: TenderSearchService, initial_prompt: Optional[str] = None):
    current_prompt = initial_prompt
    while True:
        if not current_prompt:
            try:
                current_prompt = input("\n🔍 Enter search query (or press Enter for all tenders, 'q' to quit): ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting TenderBee. Goodbye!")
                sys.exit(0)

            if current_prompt.lower() in ("q", "quit", "exit"):
                print("\nExiting TenderBee. Goodbye!")
                sys.exit(0)

        if current_prompt:
            res = service.search_by_prompt(current_prompt)
        else:
            res = service.search(TenderSearchFilter())

        results = res.get("results", [])
        display_search_results(results, query_info=f'"{current_prompt}"' if current_prompt else "All Tenders")

        if not results:
            current_prompt = None
            continue

        # Allow user to pick a tender from the list
        while True:
            try:
                user_pick = input(f"\n👉 Select tender [1-{len(results)}] to inspect, [s] new search, or [q] quit: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting TenderBee. Goodbye!")
                sys.exit(0)

            if user_pick.lower() in ("q", "quit", "exit"):
                print("\nExiting TenderBee. Goodbye!")
                sys.exit(0)
            if user_pick.lower() in ("s", "search", "n", "new"):
                current_prompt = None
                break

            try:
                idx = int(user_pick)
                if 1 <= idx <= len(results):
                    chosen_tender = results[idx - 1]
                    t_num = chosen_tender["tender_number"]

                    # Ask for view mode
                    print(f"\nSelected Tender [{idx}]: {chosen_tender['title'][:70]}...")
                    print("Choose view mode:")
                    print("  [1] Skimmed  (Fast overview, high-level financials, dates & buyer)")
                    print("  [2] Detailed (Deep PDF parsing, verbatim clauses, eligibility & rule pack)")
                    print("  [3] JSON     (Raw structured JSON schema payload)")
                    
                    try:
                        mode_input = input("Select mode [1/2/3 or s/d/j] (default: 1): ").strip().lower()
                    except (KeyboardInterrupt, EOFError):
                        print("\nExiting TenderBee. Goodbye!")
                        sys.exit(0)

                    if mode_input in ("3", "j", "json"):
                        chosen_mode = "json"
                    elif mode_input in ("2", "d", "detailed"):
                        chosen_mode = "detailed"
                    else:
                        chosen_mode = "skim"
                    interactive_tender_inspection(service, t_num, default_mode=chosen_mode)

                    # Re-display results after returning from tender inspection
                    display_search_results(results, query_info=f'"{current_prompt}"' if current_prompt else "All Tenders")
                else:
                    print(f"Please enter a number between 1 and {len(results)}.")
            except ValueError:
                print("Invalid input. Please enter a number, 's' for new search, or 'q' to quit.")


def main():
    parser = argparse.ArgumentParser(description="TenderBee Multi-Criteria Tender Discovery & Inspection CLI")
    parser.add_argument("prompt", nargs="?", default=None, help="Natural language query (e.g. 'services in haryana above 2 cr')")
    parser.add_argument("--tender", help="Look up specific tender by ID/Number (e.g. BIH/EPROC2/140751 or 2026_HRY_530295_1)")
    parser.add_argument("--mode", choices=["skim", "detailed", "json"], default="skim", help="View mode: 'skim' (basic details), 'detailed' (parse PDF), or 'json' (raw JSON payload)")
    parser.add_argument("--interactive", action="store_true", help="Force interactive mode even when parameters are given")
    parser.add_argument("--non-interactive", action="store_true", help="Disable interactive prompts (for CI/piping)")
    parser.add_argument("--state", help="Filter by Indian State (e.g. Bihar, Haryana, Maharashtra)")
    parser.add_argument("--category", choices=["Services", "Works", "Goods"], help="Filter by procurement category")
    parser.add_argument("--min-val", type=float, help="Minimum estimated contract value in INR")
    parser.add_argument("--max-val", type=float, help="Maximum estimated contract value in INR")
    parser.add_argument("--tenure", type=int, help="Minimum tenure in months")
    parser.add_argument("--city", help="City or district (e.g. Patna, Faridabad)")
    parser.add_argument("--buyer", help="Buyer or issuing authority")
    parser.add_argument("--json", action="store_true", help="Print raw JSON output and exit")

    args = parser.parse_args()
    service = TenderSearchService()

    # 1. Direct tender lookup via --tender flag
    if args.tender:
        is_interactive = (sys.stdin.isatty() or args.interactive) and not args.json and not getattr(args, 'non_interactive', False)
        if is_interactive:
            interactive_tender_inspection(service, args.tender, default_mode=args.mode)
            return

        lookup_mode = "detailed" if args.mode in ("detailed", "json") else "skim"
        result = service.get_tender(args.tender, mode=lookup_mode)
        if not result:
            print(f"❌ Tender '{args.tender}' not found.")
            sys.exit(1)

        if args.json or args.mode == "json":
            display_json_view(result)
            return

        if args.mode == "detailed":
            display_detailed_view(result)
        else:
            display_skimmed_view(result)
        return

    # 2. JSON or Non-interactive query execution
    is_interactive = (sys.stdin.isatty() or args.interactive) and not args.json and not getattr(args, 'non_interactive', False)

    if not is_interactive:
        if args.prompt:
            result = service.search_by_prompt(args.prompt)
        else:
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

        display_search_results(result.get("results", []), query_info=args.prompt or "Filters applied")
        return

    # 3. Interactive CLI search and inspection loop
    interactive_search_loop(service, initial_prompt=args.prompt)


if __name__ == "__main__":
    main()
