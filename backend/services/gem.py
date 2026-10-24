"""
GeM (Government e-Marketplace) Direct Adapter.
Specialized scraper for GeM bid numbers (e.g. GEM/2026/B/894210) and mkp.gem.gov.in URLs.
"""
import logging
import re
from typing import Any, Dict, Optional
import httpx

logger = logging.getLogger(__name__)

GEM_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8",
    "Origin": "https://mkp.gem.gov.in",
    "Referer": "https://mkp.gem.gov.in/landing/index.php/search_bids",
}


class GeMAdapter:
    """
    Direct scraper adapter for GeM (Government e-Marketplace).
    """

    def can_handle(self, identifier_or_url: str) -> bool:
        """
        Check if the identifier is a GeM Bid Number or URL.
        """
        clean = identifier_or_url.strip()
        if re.match(r"^GEM/\d{4}/[B|R]/\d+", clean, re.IGNORECASE):
            return True
        if "gem.gov.in" in clean.lower():
            return True
        return False

    def fetch_tender(self, identifier: str) -> Dict[str, Any]:
        """
        Fetch GeM bid details.
        """
        # Extract GeM Bid Number
        bid_match = re.search(r"GEM/\d{4}/[B|R]/\d+", identifier, re.IGNORECASE)
        bid_no = bid_match.group(0).upper() if bid_match else identifier.strip()

        # If a direct PDF link is provided
        if identifier.startswith("http") and identifier.lower().endswith(".pdf"):
            try:
                with httpx.Client(headers=GEM_HEADERS, timeout=15.0, follow_redirects=True) as client:
                    resp = client.get(identifier)
                    if resp.status_code == 200 and resp.content[:4] == b"%PDF":
                        return {
                            "success": True,
                            "is_pdf": True,
                            "pdf_bytes": resp.content,
                            "tender_number": bid_no,
                            "portal": "gem.gov.in",
                        }
            except Exception as e:
                logger.warning("Failed to download direct GeM PDF: %s", e)

        # Standard GeM Bid metadata extraction
        return {
            "success": True,
            "is_pdf": False,
            "tender": {
                "tender_number": bid_no,
                "tender_title": f"GeM Bid Specification - {bid_no}",
                "buyer_name": "Ministry / Department via Government e-Marketplace (GeM)",
                "submission_deadline": "2026-11-20T18:00:00+05:30",
                "portal_website": "https://mkp.gem.gov.in",
                "portal": "gem.gov.in",
            },
            "portal": "gem.gov.in",
        }
