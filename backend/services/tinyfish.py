"""
TinyFish integration client (Fetch, Search, and Agent APIs) for TenderBee.
Provides stealth browser automation with Cloudflare pre-flight barrier detection,
threaded non-blocking SSE streaming, and strict circuit breaker protection.
"""
import io
import json
import logging
import os
import queue
import threading
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional
from dotenv import load_dotenv

load_dotenv("/home/arjun/tenderbee/.env")
load_dotenv(os.path.expanduser("~/.env"))

from tinyfish import TinyFish
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
                    "quote": {"type": "string"}
                },
                "required": ["clause_type", "quote"]
            }
        }
    },
    "required": ["tender_number", "tender_title", "submission_deadline"]
}


class BidEasyScraper:
    """
    Production scraper utilizing TinyFish browser agents and fast HTTP pre-flight checks.
    """

    def __init__(self, api_key: Optional[str] = None, storage: Optional[Any] = None):
        self.api_key = api_key or os.getenv("TINYFISH_API_KEY")
        if self.api_key:
            self.client = TinyFish(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("TINYFISH_API_KEY not set. Live web scraping will be disabled.")
        self.storage = storage

    def _detect_cloudflare_barrier(self, url: str) -> Optional[str]:
        """Fast pre-flight check for Cloudflare Turnstile bot challenges."""
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            )
            urllib.request.urlopen(req, timeout=4)
            return None
        except urllib.error.HTTPError as e:
            headers_str = str(dict(e.headers)).lower()
            if e.code == 403 and ("cf-mitigated" in headers_str or "cloudflare" in headers_str):
                return "Cloudflare Turnstile Bot Barrier ('Cf-Mitigated: challenge')"
            return None
        except Exception:
            return None

    def fetch_tender(self, identifier: str, org_id: str = "org_default", force_refresh: bool = False) -> Dict[str, Any]:
        """
        Fetches and extracts a tender by either URL or Tender Number/ID.
        1. Checks production cache first.
        2. Fast pre-flight check to detect anti-bot challenge walls without burning credits.
        3. Calls TinyFish Agent with threaded queue stream consumer and 35s circuit breaker.
        """
        identifier = identifier.strip()
        is_url = identifier.startswith("http://") or identifier.startswith("https://")

        # 1. Cache lookup
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

        # 2. Determine target URL and goal for TinyFish
        if is_url:
            target_url = identifier
            # Pre-flight check: Detect Cloudflare challenge fast before burning credits
            cf_barrier = self._detect_cloudflare_barrier(target_url)
            if cf_barrier:
                print(f"  [Scraper] 🛡️ Pre-flight: {cf_barrier} active on portal.", flush=True)
                return {
                    "success": False,
                    "error": f"Portal blocked automated access ({cf_barrier}). Please upload the Tender Notice / PDF directly.",
                    "reason_code": "EXTERNAL_UNAVAILABLE",
                    "is_cached": False,
                }

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

        if not self.client:
            return {
                "success": False,
                "error": "TINYFISH_API_KEY is not configured in environment or .env file.",
                "reason_code": "EXTERNAL_UNAVAILABLE",
                "is_cached": False,
            }

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
                    logger.error(f"TinyFish scraper worker error on {target_url}: {data}")
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
            logger.error(f"TinyFish scraper failed on {target_url}: {e}")
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

        # 3. Commit to storage if available
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
