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


def test_search_service_bihar_services(tmp_path):
    """Verify search service returns seeded Bihar service tenders."""
    storage = TenderStorage(base_dir=str(tmp_path))
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
