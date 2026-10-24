"""
Universal Multi-Engine Tender Scraper Hub.
Intelligently dispatches tender scraping across GePNIC (CPPP & State Portals),
GeM (Government e-Marketplace), and TinyFish autonomous browser agents,
seamlessly streaming downloaded notices into the deterministic PDF engine.
"""
import io
import json
import logging
from typing import Any, Dict, Optional

from backend.services.captcha import CaptchaService
from backend.services.session_pool import PortalSessionPool
from backend.services.gepnic import GePNICAdapter
from backend.services.gem import GeMAdapter
from backend.services.tinyfish import BidEasyScraper
from backend.services.storage import TenderStorage
from backend.engine.parser import TenderPDFExtractor
from backend.engine.schema import TenderPDFExtractionResult

logger = logging.getLogger(__name__)


class UniversalTenderScraper:
    """
    Production-grade multi-engine scraper combining direct portal APIs,
    cloud/AI CAPTCHA solving, session pooling, and autonomous agent fallbacks.
    """

    def __init__(
        self,
        storage: Optional[TenderStorage] = None,
        captcha_service: Optional[CaptchaService] = None,
        session_pool: Optional[PortalSessionPool] = None,
        gepnic_adapter: Optional[GePNICAdapter] = None,
        gem_adapter: Optional[GeMAdapter] = None,
        tinyfish_scraper: Optional[BidEasyScraper] = None,
        pdf_extractor: Optional[TenderPDFExtractor] = None,
    ):
        self.storage = storage or TenderStorage()
        self.captcha_service = captcha_service or CaptchaService()
        self.session_pool = session_pool or PortalSessionPool()
        self.gepnic_adapter = gepnic_adapter or GePNICAdapter(
            captcha_service=self.captcha_service,
            session_pool=self.session_pool,
        )
        self.gem_adapter = gem_adapter or GeMAdapter()
        self.tinyfish_scraper = tinyfish_scraper or BidEasyScraper(storage=self.storage)
        self.pdf_extractor = pdf_extractor or TenderPDFExtractor()

    def fetch_tender(
        self,
        identifier: str,
        org_id: str = "org_default",
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Main entry point:
        1. Checks local tiered snapshot cache (sub-second hit).
        2. Routes to appropriate portal adapter (GeM, GePNIC, or TinyFish).
        3. If PDF is acquired, parses with anti-hallucination PDF extractor.
        4. Saves snapshot and returns standardized extraction dict.
        """
        # Step 1: Check cache
        if not force_refresh:
            cached_snapshot = self.storage.get_snapshot_by_tender_number(tender_number=identifier, org_id=org_id)
            if cached_snapshot:
                logger.info("Universal scraper cache hit for '%s'", identifier)
                return {
                    "success": True,
                    "is_cached": True,
                    "tender": cached_snapshot,
                }

        # Step 2: Route to specialized adapter
        logger.info("Routing intake query '%s'", identifier)
        if self.gem_adapter.can_handle(identifier):
            logger.info("Dispatched to GeMAdapter")
            adapter_res = self.gem_adapter.fetch_tender(identifier)
        elif self.gepnic_adapter.can_handle(identifier):
            logger.info("Dispatched to GePNICAdapter")
            adapter_res = self.gepnic_adapter.fetch_tender(identifier)
        else:
            logger.info("Dispatched to TinyFish autonomous agent fallback")
            return self.tinyfish_scraper.fetch_tender(
                identifier=identifier, org_id=org_id, force_refresh=force_refresh
            )

        if not adapter_res.get("success"):
            return adapter_res

        # Step 3: Handle downloaded PDF if returned by adapter
        if adapter_res.get("is_pdf") and adapter_res.get("pdf_bytes"):
            pdf_bytes = adapter_res["pdf_bytes"]
            extraction: TenderPDFExtractionResult = self.pdf_extractor.extract_from_pdf(pdf_bytes)
            tender_dict = self._format_extraction_to_tender_dict(extraction, identifier)
            raw_payload = f"Extracted from direct PDF via adapter: {adapter_res.get('portal')}"
        else:
            tender_dict = adapter_res.get("tender", {})
            raw_payload = json.dumps(tender_dict, indent=2)

        # Step 4: Persist in tiered storage
        tender_number = tender_dict.get("tender_number") or identifier
        tender_title = tender_dict.get("tender_title") or "Government Tender"
        buyer_name = tender_dict.get("buyer_name")
        deadline = tender_dict.get("submission_deadline")
        estimated_val = tender_dict.get("estimated_value_inr")

        storage_meta = self.storage.save_tender_and_snapshot(
            org_id=org_id,
            tender_number=tender_number,
            tender_title=tender_title,
            source_url=identifier,
            buyer_name=buyer_name,
            submission_deadline=deadline,
            estimated_value_inr=estimated_val,
            extracted_data=tender_dict,
            raw_text_payload=raw_payload,
        )

        return {
            "success": True,
            "is_cached": False,
            "tender": tender_dict,
            "storage": storage_meta,
            "portal": adapter_res.get("portal", "direct"),
        }

    def _format_extraction_to_tender_dict(
        self,
        extraction: TenderPDFExtractionResult,
        identifier: str,
    ) -> Dict[str, Any]:
        """
        Converts a TenderPDFExtractionResult into standardized tender dict.
        """
        return {
            "tender_number": extraction.metadata.tender_number or identifier,
            "tender_title": extraction.metadata.tender_title or "Tender Notice",
            "buyer_name": extraction.metadata.buyer_name or "Procurement Authority",
            "submission_deadline": extraction.metadata.submission_deadline or "2026-12-31T15:00:00+05:30",
            "estimated_value_inr": extraction.metadata.estimated_value_inr,
            "emd_amount_inr": extraction.metadata.emd_amount_inr,
            "mse_exemption_allowed": extraction.eligibility_rules.mse_exemption_allowed,
            "mandatory_documents": [d.value if hasattr(d, "value") else str(d) for d in extraction.mandatory_documents],
            "eligibility_rules": {
                "min_annual_turnover_inr": extraction.eligibility_rules.min_annual_turnover_inr,
                "turnover_years": extraction.eligibility_rules.turnover_years,
                "min_liquidity_inr": extraction.eligibility_rules.min_liquidity_inr,
                "min_work_experience_inr": extraction.eligibility_rules.min_work_experience_inr,
                "udin_mandatory": extraction.eligibility_rules.udin_mandatory,
                "required_nic_prefixes": extraction.eligibility_rules.required_nic_prefixes,
                "eligible_entity_types": extraction.eligibility_rules.eligible_entity_types,
            },
            "verbatim_clauses": [c.model_dump() for c in extraction.verbatim_clauses],
            "source_type": "pdf_direct_extraction",
        }
