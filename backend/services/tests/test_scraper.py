"""
Unit and integration tests for TenderBee's multi-engine scraper system:
- CaptchaService (Cloud Vision & Mock)
- PortalSessionPool (Session persistence and TTL expiry)
- GePNICAdapter & GeMAdapter
- UniversalTenderScraper routing and storage caching
"""
import time
import pytest
from backend.services.captcha import CaptchaService
from backend.services.session_pool import PortalSessionPool
from backend.services.gepnic import GePNICAdapter
from backend.services.gem import GeMAdapter
from backend.services.scraper import UniversalTenderScraper
from backend.services.storage import TenderStorage
from backend.apps.tenders.services import TenderService


def test_captcha_mock_solver():
    """Verify deterministic mock CAPTCHA solver."""
    service = CaptchaService(mock_mode=True)
    res = service.solve(b"dummy_captcha_image_bytes")
    assert isinstance(res, str)
    assert len(res) == 6
    assert res == res.upper()


def test_session_pool_lifecycle():
    """Verify session pool save, retrieve, TTL expiration, and invalidation."""
    pool = PortalSessionPool()
    pool.clear()

    # 1. Save session
    domain = "eprocure.gov.in"
    cookies = {"ASP.NET_SessionId": "test_session_123"}
    session = pool.save_session(domain=domain, cookies=cookies, ttl_seconds=1)

    assert session.domain == domain
    assert session.cookies["ASP.NET_SessionId"] == "test_session_123"

    # 2. Retrieve session before expiry
    hit = pool.get_session(domain)
    assert hit is not None
    assert hit.cookies == cookies

    # 3. Test expiry
    time.sleep(1.1)
    expired = pool.get_session(domain)
    assert expired is None

    # 4. Invalidation
    pool.save_session(domain=domain, cookies=cookies, ttl_seconds=60)
    assert pool.get_session(domain) is not None
    pool.invalidate(domain)
    assert pool.get_session(domain) is None


def test_gem_adapter_can_handle_and_fetch():
    """Verify GeMAdapter identifier detection and metadata extraction."""
    adapter = GeMAdapter()

    assert adapter.can_handle("GEM/2026/B/894210") is True
    assert adapter.can_handle("gem/2025/r/112233") is True
    assert adapter.can_handle("https://mkp.gem.gov.in/landing/index.php/search_bids") is True
    assert adapter.can_handle("2026_RAIL_99999") is False

    res = adapter.fetch_tender("GEM/2026/B/894210")
    assert res["success"] is True
    assert res["tender"]["tender_number"] == "GEM/2026/B/894210"
    assert "GeM" in res["tender"]["buyer_name"]


def test_gepnic_adapter_can_handle():
    """Verify GePNIC adapter routes CPPP and NIC portals."""
    adapter = GePNICAdapter()

    assert adapter.can_handle("https://eprocure.gov.in/eprocure/app") is True
    assert adapter.can_handle("https://mahatenders.gov.in/nicgep/app") is True
    assert adapter.can_handle("2026_RAIL_123456") is True
    assert adapter.can_handle("CPPP/2026/SERVICE/01") is True
    assert adapter.can_handle("GEM/2026/B/123456") is False


def test_universal_scraper_routing_and_caching(tmp_path):
    """Verify UniversalTenderScraper routes GeM and GePNIC queries and caches snapshots."""
    storage = TenderStorage(base_dir=str(tmp_path / "s1"))

    scraper = UniversalTenderScraper(storage=storage)

    # 1. Fetch GeM tender
    gem_id = "GEM/2026/B/778899"
    res1 = scraper.fetch_tender(gem_id)
    assert res1["success"] is True
    assert res1["is_cached"] is False
    assert res1["tender"]["tender_number"] == gem_id

    # 2. Subsequent query should hit tiered storage cache
    res2 = scraper.fetch_tender(gem_id)
    assert res2["success"] is True
    assert res2["is_cached"] is True
    assert res2["tender"]["tender_number"] == gem_id


def test_tender_service_integration_with_universal_scraper(tmp_path):
    """Verify TenderService seamlessly works with UniversalTenderScraper."""
    storage = TenderStorage(base_dir=str(tmp_path / "s2"))

    service = TenderService(storage=storage)

    gem_id = "GEM/2026/B/990011"
    intake_res = service.intake_tender(identifier=gem_id, org_id="test_org")

    assert intake_res["success"] is True
    assert intake_res["tender_number"] == gem_id
    assert intake_res["rule_pack_id"].startswith("rp_")
    assert intake_res["rule_pack"]["status"] == "DRAFT"


def test_pdf_downloader_local_and_samples():
    """Verify TenderPDFDownloader fetches local and sample PDFs."""
    from backend.services.pdf_downloader import TenderPDFDownloader

    downloader = TenderPDFDownloader()

    # Direct file path
    pdf_bytes = downloader.download_pdf("samples/western_railway_mech_tpa_2026.pdf")
    assert pdf_bytes is not None
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 100000

    # Matching tender number from samples
    pdf_bytes_matched = downloader.download_pdf("western_railway")
    assert pdf_bytes_matched is not None
    assert pdf_bytes_matched[:4] == b"%PDF"


def test_bideasy_scraper_currency_parser():
    """Verify BidEasyScraper currency normalization for Cr, Lakhs, commas, and formatted INR strings."""
    from backend.services.tinyfish import BidEasyScraper

    assert BidEasyScraper._parse_currency_value("₹ 1,33,68,44,415") == 1336844415.0
    assert BidEasyScraper._parse_currency_value("12.5 Cr") == 125000000.0
    assert BidEasyScraper._parse_currency_value("2.5 Crores") == 25000000.0
    assert BidEasyScraper._parse_currency_value("50 Lakhs") == 5000000.0
    assert BidEasyScraper._parse_currency_value("15 Lacs") == 1500000.0
    assert BidEasyScraper._parse_currency_value(1500000) == 1500000.0
    assert BidEasyScraper._parse_currency_value(None) is None
    assert BidEasyScraper._parse_currency_value("N/A") is None


def test_bideasy_scraper_cloudflare_turnstile_detection(monkeypatch):
    """Verify pre-flight circuit breaker detects Cloudflare Turnstile challenge and headers."""
    import urllib.request
    import urllib.error
    from backend.services.tinyfish import BidEasyScraper

    scraper = BidEasyScraper()

    # Case 1: Body contains turnstile challenge
    class MockResp:
        def read(self, _size):
            return b"<html><body><div class='cf-turnstile' data-sitekey='xxx'></div></body></html>"
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: MockResp())
    barrier = scraper._detect_cloudflare_barrier("https://eprocure.gov.in/test")
    assert barrier is not None
    assert "Turnstile" in barrier

    # Case 2: HTTP 403 with cf-mitigated header
    class MockHTTPError(urllib.error.HTTPError):
        def __init__(self):
            super().__init__("https://eprocure.gov.in/test", 403, "Forbidden", {"cf-mitigated": "challenge"}, None)

    def raise_http_error(*args, **kwargs):
        raise MockHTTPError()

    monkeypatch.setattr(urllib.request, "urlopen", raise_http_error)
    barrier2 = scraper._detect_cloudflare_barrier("https://eprocure.gov.in/test")
    assert barrier2 is not None
    assert "Cf-Mitigated" in barrier2

    # Case 3: Normal clean response
    class MockCleanResp:
        def read(self, _size):
            return b"<html><body><h1>Tender Portal</h1></body></html>"
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout: MockCleanResp())
    barrier3 = scraper._detect_cloudflare_barrier("https://clean-portal.gov.in")
    assert barrier3 is None


def test_bideasy_scraper_preflight_circuit_breaker(monkeypatch, tmp_path):
    """Verify fetch_tender triggers pre-flight circuit breaker before calling agent."""
    from backend.services.tinyfish import BidEasyScraper
    from backend.services.storage import TenderStorage

    storage = TenderStorage(base_dir=str(tmp_path / "bideasy"))
    scraper = BidEasyScraper(storage=storage)

    # Mock _detect_cloudflare_barrier returning a barrier
    monkeypatch.setattr(scraper, "_detect_cloudflare_barrier", lambda url: "Cloudflare Turnstile Bot Barrier ('Cf-Mitigated: challenge')")

    res = scraper.fetch_tender("2026_TEST_12345")
    assert res["success"] is False
    assert res["reason_code"] == "EXTERNAL_UNAVAILABLE"
    assert "blocked automated access" in res["error"]


