"""
Unit and integration tests for Tender Discovery & Multi-Criteria Search Engine:
- QueryParser NLP parsing (state, category, capital, tenure)
- Multi-criteria SQL filtering in TenderStorage
- End-to-end TenderSearchService
"""
import pytest
from backend.apps.tenders.search import QueryParser, TenderSearchService, TenderSearchFilter
from backend.services.storage import TenderStorage


def test_query_parser_bihar_services():
    """Verify natural language parsing for services in Bihar."""
    filters = QueryParser.parse("give me tenders related to services in bihar")
    assert filters.state == "Bihar"
    assert filters.category == "Services"
    assert filters.query is None


def test_query_parser_capital_and_tenure():
    """Verify parsing of Indian currency and tenure durations."""
    filters = QueryParser.parse("civil works in patna above 5 cr for 2 years")
    assert filters.state == "Bihar"
    assert filters.city_or_district == "Patna"
    assert filters.category == "Works"
    assert filters.min_value_inr == 50000000.0  # 5 Crore
    assert filters.min_tenure_months == 24       # 2 Years


def test_query_parser_lakhs_and_months():
    """Verify parsing of Lakhs and months."""
    filters = QueryParser.parse("security services below 50 lakhs for 6 months")
    assert filters.category == "Services"
    assert filters.max_value_inr == 5000000.0   # 50 Lakhs
    assert filters.min_tenure_months == 6


def _seed_test_tenders(storage: TenderStorage):
    import sqlite3
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    samples = [
        (
            "ut_fixture_01", "org_default", "UT/2026/01",
            "Sanitation & Waste Management Services",
            "Urban Development Department", "2026-11-28T15:00:00+05:30",
            34500000.0, "https://test.local/1", now, now,
            "Bihar", "Services", 24, 690000.0, "Patna", "eproc2.bihar.gov.in"
        ),
        (
            "ut_fixture_02", "org_default", "UT/2026/02",
            "Substation Security Guarding Services",
            "Power Holding Authority", "2026-11-22T17:00:00+05:30",
            25000000.0, "https://test.local/2", now, now,
            "Bihar", "Services", 12, 360000.0, "Gaya", "eproc2.bihar.gov.in"
        ),
    ]
    with sqlite3.connect(storage.db_path) as conn:
        conn.executemany("""
            INSERT INTO tenders (
                tender_id, organization_id, external_id, title, buyer_name,
                submission_deadline, estimated_value_inr, source_url,
                created_at, updated_at, state, category, tenure_months,
                emd_amount_inr, location, portal
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, samples)


def test_search_service_bihar_services(tmp_path):
    """Verify search service returns seeded Bihar service tenders."""
    storage = TenderStorage(base_dir=str(tmp_path))
    _seed_test_tenders(storage)
    service = TenderSearchService(storage=storage)

    res = service.search_by_prompt("tenders related to services in bihar")
    assert res["success"] is True
    assert res["total_matches"] >= 2
    for tender in res["results"]:
        assert tender["state"] == "Bihar"
        assert tender["category"] == "Services"


def test_search_service_multi_criteria_filter(tmp_path):
    """Verify filtering strictly on capital and tenure."""
    storage = TenderStorage(base_dir=str(tmp_path))
    _seed_test_tenders(storage)
    service = TenderSearchService(storage=storage)

    filters = TenderSearchFilter(
        state="Bihar",
        min_value_inr=20000000.0,  # >= 2 Cr
        min_tenure_months=12,
    )
    res = service.search(filters)
    assert res["success"] is True
    assert res["total_matches"] >= 2
    for tender in res["results"]:
        assert tender["state"] == "Bihar"
        assert tender["estimated_value_inr"] >= 20000000.0
        assert tender["tenure_months"] >= 12


def test_query_parser_uttar_pradesh_and_aliases():
    """Verify parsing of Uttar Pradesh, UP alias, and clean residual keywords."""
    f1 = QueryParser.parse("services tender in uttar pradesh")
    assert f1.state == "Uttar Pradesh"
    assert f1.category == "Services"
    assert f1.query is None

    f2 = QueryParser.parse("uttar pradesh")
    assert f2.state == "Uttar Pradesh"
    assert f2.query is None

    f3 = QueryParser.parse("up")
    assert f3.state == "Uttar Pradesh"
    assert f3.query is None


def test_query_parser_rajasthan_and_jaipur():
    """Verify parsing of Rajasthan, alias rj, and city-based state inference for Jaipur."""
    f1 = QueryParser.parse("rajasthan")
    assert f1.state == "Rajasthan"
    assert f1.query is None

    f2 = QueryParser.parse("works in jaipur above 10 cr")
    assert f2.state == "Rajasthan"
    assert f2.city_or_district == "Jaipur"
    assert f2.category == "Works"
    assert f2.min_value_inr == 100000000.0




def test_search_service_live_discovery_fallback(tmp_path):
    """Verify live search fallback when local index has no matches for a query."""
    storage = TenderStorage(base_dir=str(tmp_path))

    # Mock or direct live search engine
    class MockLiveSearchEngine:
        def search_live(self, query=None, state=None, category=None, city=None, raw_prompt=None, limit=10):
            return [{
                "tender_id": "tnd_live_mock_1",
                "tender_number": "SIK/2026/001",
                "title": "Supply of Healthcare Equipment in Gangtok",
                "buyer_name": "Health Department Government of Sikkim",
                "state": "Sikkim",
                "category": "Goods",
                "estimated_value_inr": 25000000.0,
                "portal": "sikkimtender.gov.in",
            }]

    service = TenderSearchService(storage=storage, live_search_engine=MockLiveSearchEngine())
    res = service.search_by_prompt("sikkim goods tender")
    assert res["total_matches"] == 1
    assert res["source"] == "live_portal_discovery"
    assert res["results"][0]["state"] == "Sikkim"
    assert res["results"][0]["tender_number"] == "SIK/2026/001"

