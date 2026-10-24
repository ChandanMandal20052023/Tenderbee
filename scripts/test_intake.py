"""
CLI test script for TenderBee Tender Intake & Rule-Pack Ingestion.
Supports either a Tender URL OR a Tender Number / ID!

Usage:
    .venv/bin/python scripts/test_intake.py [TENDER_URL_OR_NUMBER] [--json]

Examples:
    .venv/bin/python scripts/test_intake.py "GEM/2026/B/894210"
    .venv/bin/python scripts/test_intake.py "https://tenders.infralens.in/tender/GEM-2026-B-894210"
    .venv/bin/python scripts/test_intake.py "GEM/2026/B/894210" --json
"""
import sys
import os
import json
import time

# Ensure project root is in sys.path
sys.path.insert(0, "/home/arjun/tenderbee")

from tenderbee.apps.tenders.service import TenderService


def main():
    args = [a for a in sys.argv[1:] if a != "--json"]
    json_only = "--json" in sys.argv

    default_identifier = "GEM/2026/B/894210"
    identifier = args[0] if args else default_identifier

    service = TenderService()

    # Step 1: Intake tender by URL or Tender Number
    start_time = time.time()
    result = service.intake_tender(identifier=identifier, org_id="demo_org")
    elapsed = time.time() - start_time

    if not result.get("success"):
        if json_only:
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Intake failed: {result.get('error')}")
        return

    # If user passed --json, print pure formatted JSON and exit
    if json_only:
        print(json.dumps(result, indent=2, default=str))
        return

    # Otherwise print full detailed CLI output
    is_url = identifier.startswith("http://") or identifier.startswith("https://")
    print("=" * 75)
    print("TENDERBEE TENDER INTAKE ENGINE")
    print(f"Input Type    : {'URL' if is_url else 'Tender Number'}")
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

    # Step 4: Full JSON Schema Output
    print("\n--- STEP 4: EXTRACTED JSON SCHEMA PAYLOAD ---")
    print(json.dumps(result, indent=2, default=str))
    print("=" * 75)


if __name__ == "__main__":
    main()
