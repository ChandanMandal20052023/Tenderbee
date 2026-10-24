"""
Production Scraper Module for TenderBee.
Integrates TinyFish Agent with tiered storage, content-addressed caching,
and strict Pydantic validation.
"""
import os
import json
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv("/home/arjun/tenderbee/.env")
load_dotenv(os.path.expanduser("~/.env"))

from tinyfish import TinyFish
from tenderbee.apps.tenders.storage import TenderStorage
from tenderbee.apps.tenders.validators import validate_identifier

logger = logging.getLogger(__name__)


# Schema for TinyFish Agent extraction
TENDER_DETAIL_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "tender_number": {"type": "string"},
        "tender_title": {"type": "string"},
        "buyer_name": {"type": "string"},
        "buyer_location": {"type": "string", "nullable": True},
        "submission_deadline": {"type": "string"},
        "bid_opening_date": {"type": "string", "nullable": True},
        "estimated_value_inr": {"type": "number", "nullable": True},
        "emd_amount_inr": {"type": "number", "nullable": True},
        "mse_exemption_allowed": {"type": "boolean"},
        "mandatory_documents": {
            "type": "array",
            "items": {"type": "string"}
        },
        "eligibility_rules": {
            "type": "object",
            "properties": {
                "min_annual_turnover_inr": {"type": "number", "nullable": True},
                "turnover_years": {"type": "integer"},
                "udin_mandatory": {"type": "boolean"},
                "required_nic_prefixes": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["turnover_years", "udin_mandatory"]
        },
        "verbatim_clauses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "clause_type": {"type": "string"},
                    "quote": {"type": "string"},
                    "section_or_page": {"type": "string", "nullable": True}
                },
                "required": ["clause_type", "quote"]
            }
        }
    },
    "required": ["tender_number", "tender_title", "buyer_name", "submission_deadline"]
}


class BidEasyScraper:
    def __init__(self, api_key: Optional[str] = None, storage: Optional[TenderStorage] = None):
        self.api_key = api_key or os.getenv("TINYFISH_API_KEY")
        if not self.api_key:
            raise ValueError("TINYFISH_API_KEY not found in environment or .env file.")
        
        self.client = TinyFish(api_key=self.api_key)
        self.storage = storage or TenderStorage()

    def fetch_tender(self, identifier: str, org_id: str = "org_default", force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetches and extracts a tender by either URL or Tender Number/ID.
        1. Checks production cache first (instant response if already ingested).
        2. Calls TinyFish Agent with anti-bot bypass & schema enforcement.
        3. Commits immutable snapshot and relational metadata to storage.
        """
        identifier = identifier.strip()
        
        # 0. Format and Security Validation
        validation = validate_identifier(identifier)
        if not validation.is_valid:
            return {
                "success": False,
                "error": validation.error_message,
                "input_type": validation.input_type,
                "is_cached": False,
            }

        is_url = validation.input_type == "URL"

        # 1. Cache lookup
        if not force_refresh:
            cached = (
                self.storage.get_snapshot_by_url(identifier, org_id=org_id)
                if is_url
                else self.storage.get_snapshot_by_tender_number(identifier, org_id=org_id)
            )
            if cached:
                return {
                    "success": True,
                    "is_cached": True,
                    "tender": cached,
                }

        # 2. Determine target URL and goal for TinyFish
        if is_url:
            target_url = identifier
            goal = (
                "Analyze this Indian tender page in full detail. Extract the tender/bid number, "
                "work title, procuring buyer organization, closing submission deadline, "
                "estimated value in INR, EMD amount, whether MSME/MSE bidders get exemption, "
                "mandatory documents required, minimum annual turnover threshold and number of years, "
                "whether CA UDIN is mandatory, any required NIC codes, and copy the verbatim quotes "
                "for each eligibility clause."
            )
        else:
            target_url = f"https://tenders.infralens.in/?q={identifier}"
            goal = (
                f"Search for tender number '{identifier}' on this page. Find the exact matching tender card, "
                "open its details page, and extract the tender/bid number, work title, procuring buyer organization, "
                "closing submission deadline, estimated value in INR, EMD amount, whether MSME/MSE bidders get exemption, "
                "mandatory documents required, minimum annual turnover threshold and number of years, "
                "whether CA UDIN is mandatory, any required NIC codes, and copy the verbatim quotes for each eligibility clause."
            )

        extracted_result = None
        raw_stream_text = []

        try:
            with self.client.agent.stream(
                url=target_url,
                goal=goal,
                output_schema=TENDER_DETAIL_OUTPUT_SCHEMA,
            ) as stream:
                for event in stream:
                    event_type = getattr(event, "type", "EVENT")
                    msg = getattr(event, "message", "")
                    if msg:
                        print(f"  [TinyFish] {event_type}: {msg}", flush=True)
                        raw_stream_text.append(msg)
                    else:
                        print(f"  [TinyFish] {event_type}", flush=True)
                    if hasattr(event, "result_json") and event.result_json:
                        extracted_result = event.result_json
                    elif hasattr(event, "result") and event.result:
                        extracted_result = event.result
        except Exception as e:
            logger.error(f"TinyFish scraper failed on {target_url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "is_cached": False,
            }

        if not extracted_result:
            return {
                "success": False,
                "error": "TinyFish completed without returning structured tender output.",
                "is_cached": False,
            }

        # 3. Commit to production tiered storage
        tender_number = extracted_result.get("tender_number") or f"TND-{hash(target_url) % 1000000}"
        tender_title = extracted_result.get("tender_title") or "Government Tender"
        buyer_name = extracted_result.get("buyer_name")
        deadline = extracted_result.get("submission_deadline")
        estimated_val = extracted_result.get("estimated_value_inr")

        storage_meta = self.storage.save_tender_and_snapshot(
            org_id=org_id,
            tender_number=tender_number,
            tender_title=tender_title,
            source_url=target_url,
            buyer_name=buyer_name,
            submission_deadline=deadline,
            estimated_value_inr=estimated_val,
            extracted_data=extracted_result,
            raw_text_payload="\n".join(raw_stream_text) or json.dumps(extracted_result, indent=2),
        )

        return {
            "success": True,
            "is_cached": False,
            "tender": extracted_result,
            "storage": storage_meta,
        }
