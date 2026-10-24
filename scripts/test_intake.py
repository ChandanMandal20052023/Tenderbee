"""
CLI test script for TenderBee Tender Intake & Rule-Pack Ingestion.
Supports either a Tender URL, Tender Number, or direct Document/Text file!

Usage:
    .venv/bin/python scripts/test_intake.py [TENDER_URL_OR_NUMBER] [--json]
    .venv/bin/python scripts/test_intake.py --file [TENDER_TEXT_FILE] [--json]

Examples:
    .venv/bin/python scripts/test_intake.py "GEM/2026/B/894210"
    .venv/bin/python scripts/test_intake.py "https://tenders.infralens.in/tender/GEM-2026-B-894210"
    .venv/bin/python scripts/test_intake.py --file sample_tender.txt
"""
import sys
import os
import json
import time
from pathlib import Path

# Ensure project root is in sys.path
REPO_ROOT = str(Path(__file__).resolve().parents[1])
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.apps.tenders.services import TenderService


def main():
    json_only = "--json" in sys.argv
    schema_only = "--schema" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("--json", "--schema")]

    if schema_only:
        from backend.engine.parser import TenderPDFExtractor
        print(json.dumps(TenderPDFExtractor().get_json_schema(), indent=2))
        return

    file_mode = "--file" in args
    is_pdf = False
    file_path = None
    if file_mode:
        file_idx = args.index("--file")
        if file_idx + 1 < len(args):
            file_path = args[file_idx + 1]
        else:
            print("❌ Please provide a file path after --file")
            return
        is_pdf = file_path.lower().endswith(".pdf")
        identifier = f"Document File: {file_path}"
    elif args and args[0].lower().endswith(".pdf"):
        file_mode = True
        is_pdf = True
        file_path = args[0]
        identifier = f"Document File: {file_path}"
    else:
        default_identifier = "GEM/2026/B/894210"
        identifier = args[0] if args else default_identifier

    service = TenderService()

    # Step 1: Intake tender
    start_time = time.time()
    if file_mode and is_pdf:
        result = service.intake_tender_pdf(pdf_path=file_path, org_id="demo_org")
    elif file_mode:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        result = service.intake_tender_text(text_content=content, org_id="demo_org")
    else:
        result = service.intake_tender(identifier=identifier, org_id="demo_org")
    elapsed = time.time() - start_time

    if not result.get("success"):
        if json_only:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n❌ Intake failed: {result.get('error')}")
            print(f"   Reason Code : {result.get('reason_code', 'UNKNOWN')}")
            print("   💡 Tip: When a portal is protected by Cloudflare, upload the Tender PDF or text directly using: --file <tender_file.txt>")
        return

    # If user passed --json, print pure formatted JSON and exit
    if json_only:
        print(json.dumps(result, indent=2, default=str))
        return

    # Otherwise print full detailed CLI output
    is_url = identifier.startswith("http://") or identifier.startswith("https://")
    print("=" * 75)
    print("TENDERBEE TENDER INTAKE ENGINE")
    print(f"Input Type    : {'File Upload' if file_mode else ('URL' if is_url else 'Tender Number')}")
    print(f"Identifier    : {identifier}")
    print("=" * 75)

    print(f"\n--- STEP 1: INGESTION RESULT ---")
    print(f"Status        : ✅ Success (Elapsed: {elapsed:.2f}s | Cached: {result['is_cached']})")
    print(f"Tender ID     : {result['tender_id']}")
    print(f"Tender Number : {result['tender_number']}")
    print(f"Tender Title  : {result['tender_title']}")
    print(f"Buyer Name    : {result['buyer_name']}")
    print(f"Deadline      : {result['submission_deadline']}")
    print(f"Rule Pack ID  : {result['rule_pack_id']}")

    print("\n--- STEP 2: PROPOSED COMPLIANCE RULES ---")
    rules = result["rule_pack"]["rules"]
    for idx, r in enumerate(rules, 1):
        print(f"\n[{idx}] Rule: {r['rule_id']} ({r['type']})")
        print(f"    Mandatory : {r['mandatory']}")
        print(f"    Params    : {json.dumps(r['params'])}")
        print(f"    Quote     : \"{r['source']['quote']}\" (Page {r['source']['page']})")

    # Step 3: Human Freeze
    print("\n--- STEP 3: HUMAN CONFIRMATION (FREEZE RULE PACK) ---")
    rp_id = result["rule_pack_id"]
    freeze_result = service.confirm_rule_pack(rp_id, confirmed_by="user_reviewer_01")
    print(f"✅ Rule Pack {rp_id} is now: {freeze_result['status']}")

    # Step 4: Verbatim Clause Citations
    extraction = result.get("extraction", {})
    clauses = extraction.get("verbatim_clauses", [])
    if clauses:
        print(f"\n--- STEP 4: VERBATIM CLAUSE CITATIONS ({len(clauses)} Found) ---")
        for c in clauses:
            print(f"  [Page {c.get('page', 1):02d}] {c.get('clause_type')}:")
            print(f"         \"{c.get('quote')}\"")

    # Step 5: Validated JSON Schema Output
    print("\n--- STEP 5: EXTRACTED JSON SCHEMA PAYLOAD ---")
    summary_output = {
        "success": result["success"],
        "tender_number": result["tender_number"],
        "tender_title": result["tender_title"],
        "buyer_name": result["buyer_name"],
        "estimated_value_inr": result.get("estimated_value_inr"),
        "emd_amount_inr": result.get("emd_amount_inr"),
        "contract_period": result.get("contract_period"),
        "portal_website": result.get("portal_website"),
        "rule_pack_id": result["rule_pack_id"],
        "rule_pack": result["rule_pack"],
        "eligibility_rules": extraction.get("eligibility_rules", {}),
        "mandatory_documents": extraction.get("mandatory_documents", []),
        "verbatim_clauses": clauses,
        "storage": result.get("storage", {}),
    }
    print(json.dumps(summary_output, indent=2, default=str))
    print("=" * 75)


if __name__ == "__main__":
    main()
