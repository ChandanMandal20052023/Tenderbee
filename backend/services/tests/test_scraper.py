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
