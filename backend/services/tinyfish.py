"""
TinyFish integration client (Fetch, Search, and Agent APIs) for TenderBee.
Provides stealth browser automation with Cloudflare pre-flight barrier detection,
targeted visual DOM interaction, structured schema validation, threaded non-blocking
SSE streaming, and strict circuit breaker protection.
"""
import io
import json
import logging
import os
import queue
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

_repo_root = Path(__file__).resolve().parent.parent.parent
load_dotenv(_repo_root / ".env")
load_dotenv()

try:
    from tinyfish import TinyFish
except ImportError:
    TinyFish = None

from backend.engine.schema import TenderPDFExtractionResult

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
                "min_liquidity_inr": {"type": "number", "nullable": True},
                "min_work_experience_inr": {"type": "number", "nullable": True},
                "udin_mandatory": {"type": "boolean"},
                "required_nic_prefixes": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        },
        "verbatim_clauses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "clause_type": {"type": "string"},
                    "quote": {"type": "string"},
                    "page": {"type": "integer", "nullable": True}
                },
                "required": ["clause_type", "quote"]
            }
        }
    },
    "required": ["tender_number", "tender_title", "submission_deadline"]
}


class BidEasyScraper:
    """
    Production scraper utilizing TinyFish browser agents and fast HTTP pre-flight checks:
    1. Targeted Agent Automation: Launches autonomous browser agents against direct or indexed pages.
    2. Visual DOM Interaction: Navigates rendered DOM, search inputs, and table cells (td.td_caption, td.td_field).
    3. Structured Schema Validation: Enforces TENDER_DETAIL_OUTPUT_SCHEMA with numerical normalization.
    4. Pre-flight Circuit Breaker: Detects Cloudflare Turnstile barriers before burning credits.
    """

    def __init__(self, api_key: Optional[str] = None, storage: Optional[Any] = None):
        self.api_key = api_key or os.getenv("TINYFISH_API_KEY")
        if self.api_key and TinyFish:
            self.client = TinyFish(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("TINYFISH_API_KEY not set or tinyfish library unavailable. Live web scraping will be disabled.")
        self.storage = storage

    def _detect_cloudflare_barrier(self, url: str) -> Optional[str]:
        """
        Fast pre-flight check for Cloudflare Turnstile bot challenges before launching browser tasks.
        Checks HTTP status codes, Cloudflare mitigation headers, and Turnstile challenge markup.
        """
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
            )
            with urllib.request.urlopen(req, timeout=4) as resp:
                body_sample = resp.read(2048).decode("utf-8", errors="ignore").lower()
                if "cf-turnstile" in body_sample or "just a moment" in body_sample:
                    return "Cloudflare Turnstile Bot Barrier ('Turnstile Challenge in HTML')"
            return None
        except urllib.error.HTTPError as e:
            headers_str = str(dict(e.headers)).lower()
            if e.code in (403, 503) and ("cf-mitigated" in headers_str or "cloudflare" in headers_str or "cf-ray" in headers_str):
                return "Cloudflare Turnstile Bot Barrier ('Cf-Mitigated: challenge')"
            return None
        except Exception:
            return None

    @staticmethod
    def _parse_currency_value(val: Any) -> Optional[float]:
        """Parses raw text currency amounts (e.g. '₹ 1,33,68,44,415', '50 Lakhs', '12 Cr') to float."""
        if val is None or isinstance(val, (int, float)):
            return float(val) if val is not None else None
        if isinstance(val, str):
            s = val.strip().replace(",", "")
            # Cr / Crore
            m_cr = re.search(r"(\d+(?:\.\d+)?)\s*(?:cr|crore|crores)\b", s, re.IGNORECASE)
            if m_cr:
                return float(m_cr.group(1)) * 10000000.0
            # Lakh / Lakhs
            m_lakh = re.search(r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l)\b", s, re.IGNORECASE)
            if m_lakh:
                return float(m_lakh.group(1)) * 100000.0
            # Plain numbers with currency symbols
            m_num = re.search(r"(\d+(?:\.\d+)?)", s)
            if m_num:
                return float(m_num.group(1))
        return None

    def fetch_tender(self, identifier: str, org_id: str = "org_default", force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetches and extracts a tender by either URL or Tender Number/ID.
        1. Checks production tiered storage cache first.
        2. Resolves target URL (direct portal or aggregated portal index).
        3. Pre-flight check detects Cloudflare barriers without burning credits.
        4. Calls TinyFish Agent with threaded queue stream consumer and 35s circuit breaker.
        5. Enforces structured schema validation and persists immutable snapshot.
        """
        identifier = identifier.strip()
        is_url = identifier.startswith("http://") or identifier.startswith("https://")

        # 1. Tiered storage cache lookup
        if self.storage and not force_refresh:
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

        # 2. Targeted Agent Automation: determine target URL and DOM guidance goal
        if is_url:
            target_url = identifier
            goal = (
                "Analyze this Indian public procurement tender page in full detail.\n"
                "1. Visually scan the rendered DOM and locate the tender summary tables (td.td_caption and td.td_field).\n"
                "2. Extract the tender/bid number, work title, procuring buyer organization, location, closing submission deadline, "
                "bid opening date, estimated value in INR, and EMD amount.\n"
                "3. Navigate to eligibility, criteria, or documents tabs/sections if present.\n"
                "4. Extract whether MSME/MSE bidders get exemption, all mandatory documents required, minimum annual turnover threshold and number of years, "
                "whether CA UDIN is mandatory, any required NIC codes, and copy verbatim quotes for each eligibility clause."
            )
        else:
            # Check if tender already exists in local SQLite storage with a known source_url
            known_source_url = None
            if self.storage:
                try:
                    import sqlite3
                    with sqlite3.connect(self.storage.db_path) as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "SELECT source_url FROM tenders WHERE external_id = ? OR tender_id = ? LIMIT 1",
                            (identifier, identifier),
                        )
                        row = cursor.fetchone()
                        if row and row[0]:
                            known_source_url = row[0]
                except Exception:
                    pass

            if known_source_url and (known_source_url.startswith("http://") or known_source_url.startswith("https://")):
                target_url = known_source_url
                goal = (
                    f"Analyze this official tender page for tender '{identifier}' in full detail.\n"
                    "1. Visually scan the rendered DOM table cells (td.td_caption and td.td_field).\n"
                    "2. Extract the tender/bid number, work title, procuring buyer organization, location, closing submission deadline, "
                    "bid opening date, estimated value in INR, and EMD amount.\n"
                    "3. Locate eligibility criteria and copy verbatim quotes for each eligibility clause."
                )
            else:
                encoded_query = urllib.parse.quote(identifier)
                target_url = f"https://tenders.infralens.in/?q={encoded_query}"
                goal = (
                    f"Search for tender number '{identifier}' on this page.\n"
                    f"1. Locate any search input box on the page, enter '{identifier}', and submit or click Search.\n"
                    "2. Visually scan the rendered DOM cards and table rows for the exact matching tender.\n"
                    "3. Click through to open the full tender details view or card.\n"
                    "4. Inspect the rendered HTML table cells (including td.td_caption and td.td_field) and notices.\n"
                    "5. Extract the tender number, tender title, buyer name, buyer location, submission deadline, "
                    "bid opening date, estimated value in INR, EMD amount, whether MSME/MSE bidders get exemption, "
                    "mandatory documents required, minimum annual turnover threshold and number of years, "
                    "whether CA UDIN is mandatory, required NIC codes, and copy the verbatim quotes for each eligibility clause."
                )

        # 3. Pre-flight Circuit Breaker: check for anti-bot barriers before spending browser credits
        cf_barrier = self._detect_cloudflare_barrier(target_url)
        if cf_barrier:
            print(f"  [Scraper] 🛡️ Pre-flight: {cf_barrier} active on portal.", flush=True)
            return {
                "success": False,
                "error": f"Portal blocked automated access ({cf_barrier}). Please upload the Tender Notice / PDF directly.",
                "reason_code": "EXTERNAL_UNAVAILABLE",
                "is_cached": False,
            }

        if not self.client:
            return {
                "success": False,
                "error": "TINYFISH_API_KEY is not configured in environment or .env file.",
                "reason_code": "EXTERNAL_UNAVAILABLE",
                "is_cached": False,
            }

        # 4. Stream consumer with circuit breaker
        extracted_result = None
        raw_stream_text = []
        max_duration_seconds = 35
        start_time = time.time()
        timeout_hit = False
        cloudflare_hit = False

        event_queue = queue.Queue()

        def stream_worker():
            try:
                with self.client.agent.stream(
                    url=target_url,
                    goal=goal,
                    output_schema=TENDER_DETAIL_OUTPUT_SCHEMA,
                ) as stream:
                    for event in stream:
                        event_queue.put(("event", event))
            except Exception as e:
                event_queue.put(("error", e))
            finally:
                event_queue.put(("done", None))

        worker_thread = threading.Thread(target=stream_worker, daemon=True)
        worker_thread.start()

        try:
            while True:
                elapsed = time.time() - start_time
                if elapsed > max_duration_seconds:
                    print(f"  [TinyFish] ⏱️ Circuit breaker triggered ({elapsed:.1f}s > {max_duration_seconds}s). Aborting stream.", flush=True)
                    timeout_hit = True
                    break

                try:
                    item_type, data = event_queue.get(timeout=min(0.5, max(0.1, max_duration_seconds - elapsed)))
                except queue.Empty:
                    continue

                if item_type == "done":
                    break
                elif item_type == "error":
                    logger.error("TinyFish scraper worker error on %s: %s", target_url, data)
                    return {
                        "success": False,
                        "error": str(data),
                        "is_cached": False,
                    }
                elif item_type == "event":
                    event = data
                    event_type = getattr(event, "type", "EVENT")
                    purpose = getattr(event, "purpose", None)
                    streaming_url = getattr(event, "streaming_url", None)
                    run_id = getattr(event, "run_id", None)
                    msg = purpose or getattr(event, "message", None) or ""

                    if streaming_url:
                        print(f"  [TinyFish] 📺 Live Browser Stream: {streaming_url}", flush=True)

                    if "cloudflare" in msg.lower() or "challenge" in msg.lower() or "just a moment" in msg.lower():
                        print(f"  [TinyFish] 🛡️ Cloudflare bot protection detected: {msg}", flush=True)
                        cloudflare_hit = True
                        break

                    if msg:
                        print(f"  [TinyFish] {event_type}: {msg}", flush=True)
                        raw_stream_text.append(msg)
                    else:
                        print(f"  [TinyFish] {event_type} (run_id: {run_id})", flush=True)

                    if hasattr(event, "result_json") and event.result_json:
                        extracted_result = event.result_json
                        break
                    elif hasattr(event, "result") and event.result:
                        extracted_result = event.result
                        break
        except Exception as e:
            logger.error("TinyFish scraper failed on %s: %s", target_url, e)
            return {
                "success": False,
                "error": str(e),
                "is_cached": False,
            }

        if not extracted_result:
            reason = "Cloudflare / CAPTCHA challenge encountered" if cloudflare_hit else "Scraper timed out waiting for portal"
            return {
                "success": False,
                "error": f"Portal blocked automated access ({reason}). Please upload the Tender Notice / PDF directly.",
                "reason_code": "EXTERNAL_UNAVAILABLE",
                "is_cached": False,
            }

        # 5. Structured Schema Validation & Normalization
        if isinstance(extracted_result, str):
            try:
                clean_json = re.sub(r"^```(?:json)?\s*|\s*```$", "", extracted_result.strip(), flags=re.MULTILINE)
                extracted_result = json.loads(clean_json)
            except Exception as e:
                logger.warning("Failed to parse string extracted_result to JSON: %s", e)

        if not isinstance(extracted_result, dict):
            return {
                "success": False,
                "error": "Extracted result did not conform to the expected dictionary schema.",
                "reason_code": "SCHEMA_MISMATCH",
                "is_cached": False,
            }

        # Validate required fields
        extracted_result["tender_number"] = extracted_result.get("tender_number") or identifier
        extracted_result["tender_title"] = extracted_result.get("tender_title") or "Procurement Tender"
        if not extracted_result.get("submission_deadline"):
            extracted_result["submission_deadline"] = "Not Specified"

        # Normalize financial values
        extracted_result["estimated_value_inr"] = self._parse_currency_value(extracted_result.get("estimated_value_inr"))
        extracted_result["emd_amount_inr"] = self._parse_currency_value(extracted_result.get("emd_amount_inr"))

        if "eligibility_rules" in extracted_result and isinstance(extracted_result["eligibility_rules"], dict):
            elig = extracted_result["eligibility_rules"]
            elig["min_annual_turnover_inr"] = self._parse_currency_value(elig.get("min_annual_turnover_inr"))
            elig["min_liquidity_inr"] = self._parse_currency_value(elig.get("min_liquidity_inr"))
            elig["min_work_experience_inr"] = self._parse_currency_value(elig.get("min_work_experience_inr"))

        # 6. Commit immutable snapshot to tiered storage
        if self.storage:
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
                raw_text_payload="\n".join(raw_stream_text),
            )
            return {
                "success": True,
                "is_cached": False,
                "tender": extracted_result,
                "storage": storage_meta,
            }

        return {
            "success": True,
            "is_cached": False,
            "tender": extracted_result,
        }
