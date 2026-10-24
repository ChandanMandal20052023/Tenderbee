"""
Universal Tender PDF Downloader.
Acquires the official tender notice PDF from government procurement portals:
- GeM (Government e-Marketplace direct document endpoints)
- GePNIC / CPPP (eprocure.gov.in and state portals with session cookie preservation)
- Direct PDF URLs and local sample documents
"""
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
import httpx

from backend.services.session_pool import PortalSessionPool

logger = logging.getLogger(__name__)

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/pdf, text/html, application/xhtml+xml, */*",
    "Accept-Language": "en-IN,en;q=0.9",
}


class TenderPDFDownloader:
    """
    Downloads raw tender notice PDFs from government websites.
    """

    def __init__(self, session_pool: Optional[PortalSessionPool] = None):
        self.session_pool = session_pool or PortalSessionPool()

    def download_pdf(self, identifier_or_url: str) -> Optional[bytes]:
        """
        Main entrypoint: resolves identifier or URL and returns raw PDF bytes (%PDF...).
        Returns None if document could not be retrieved.
        """
        target = identifier_or_url.strip()

        # 1. Local file path check
        if os.path.exists(target) and target.lower().endswith(".pdf"):
            logger.info("Loading tender PDF from local filesystem: %s", target)
            with open(target, "rb") as f:
                return f.read()

        # 2. Check if it's a GeM Bid ID (e.g. GEM/2026/B/894210)
        gem_m = re.search(r"GEM/\d{4}/[B|R]/(\d+)", target, re.IGNORECASE)
        if gem_m:
            bid_id = gem_m.group(0)
            logger.info("Attempting direct GeM PDF download for %s", bid_id)
            pdf_bytes = self._download_gem_bid_pdf(bid_id)
            if pdf_bytes:
                return pdf_bytes

        # 3. Direct HTTP(S) URL
        if target.startswith("http://") or target.startswith("https://"):
            return self._download_from_url(target)

        # 4. Check known samples directory
        samples_dir = Path(__file__).resolve().parents[2] / "samples"
        for sample_pdf in samples_dir.glob("*.pdf"):
            # Check if tender identifier is inside the sample filename
            clean_id = re.sub(r"[^\w]", "", target.lower())
            clean_name = re.sub(r"[^\w]", "", sample_pdf.stem.lower())
            if clean_id in clean_name or clean_name in clean_id:
                logger.info("Found matching tender PDF in samples: %s", sample_pdf)
                with open(sample_pdf, "rb") as f:
                    return f.read()

        logger.warning("Could not download or locate tender PDF for '%s'", target)
        return None

    def _download_gem_bid_pdf(self, bid_id: str) -> Optional[bytes]:
        """
        Attempts to fetch GeM bid document from official endpoints.
        """
        clean_bid = urllib_safe_bid = bid_id.replace("/", "-")
        candidate_urls = [
            f"https://bidplus.gem.gov.in/showbidDocument/{urllib_safe_bid}",
            f"https://bidplus.gem.gov.in/showbidDocument/{bid_id}",
            f"https://mkp.gem.gov.in/landing/index.php/download_bid_doc/{bid_id}",
        ]
        with httpx.Client(headers=BROWSER_HEADERS, timeout=15.0, follow_redirects=True) as client:
            for url in candidate_urls:
                try:
                    resp = client.get(url)
                    if resp.status_code == 200 and resp.content[:4] == b"%PDF":
                        logger.info("Successfully fetched GeM PDF from %s", url)
                        return resp.content
                except Exception as e:
                    logger.debug("GeM candidate url failed (%s): %s", url, e)
        return None

    def _download_from_url(self, url: str) -> Optional[bytes]:
        """
        Downloads PDF directly from a web URL using session cookies if available.
        """
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc

        session = self.session_pool.get_session(domain)
        cookies = session.cookies if session else {}

        with httpx.Client(headers=BROWSER_HEADERS, cookies=cookies, timeout=20.0, follow_redirects=True) as client:
            try:
                resp = client.get(url)
                if resp.status_code == 200 and (resp.content[:4] == b"%PDF" or "application/pdf" in resp.headers.get("content-type", "")):
                    logger.info("Successfully downloaded tender PDF from %s (%d bytes)", url, len(resp.content))
                    return resp.content

                # If HTML returned, check for embedded PDF link (GePNIC Tendernotice)
                if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
                    html = resp.text
                    pdf_link = self._extract_pdf_link_from_html(html, url)
                    if pdf_link:
                        logger.info("Found embedded PDF link in HTML: %s", pdf_link)
                        doc_resp = client.get(pdf_link)
                        if doc_resp.status_code == 200 and doc_resp.content[:4] == b"%PDF":
                            return doc_resp.content
            except Exception as e:
                logger.error("Failed to download PDF from %s: %s", url, e)

        return None

    def _extract_pdf_link_from_html(self, html: str, base_url: str) -> Optional[str]:
        """
        Extracts tender notice download link from GePNIC / CPPP details page.
        """
        import urllib.parse
        # Matches Tendernotice_1.pdf or links ending in .pdf
        match = re.search(r'href=["\']([^"\']+\.pdf[^"\']*)["\']', html, re.IGNORECASE)
        if match:
            return urllib.parse.urljoin(base_url, match.group(1))

        # Matches GePNIC directDocDownload action
        action_match = re.search(r'href=["\']([^"\']*directDocDownload[^"\']*)["\']', html, re.IGNORECASE)
        if action_match:
            return urllib.parse.urljoin(base_url, action_match.group(1))

        return None
