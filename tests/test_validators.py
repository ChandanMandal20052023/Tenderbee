"""Unit tests for TenderBee URL and Tender Number Validators."""
import pytest
from tenderbee.apps.tenders.validators import (
    validate_url,
    validate_tender_number,
    validate_identifier,
)


def test_valid_urls():
    valid_urls = [
        "https://tenders.infralens.in/tender/pind-2627-00220-320314",
        "https://gem.gov.in/bid/GEM/2026/B/894210",
        "https://eprocure.gov.in/eprocure/app?page=FrontEndTenderDetails",
    ]
    for url in valid_urls:
        res = validate_url(url)
        assert res.is_valid is True, f"Expected {url} to be valid, got: {res.error_message}"
        assert res.input_type == "URL"


def test_invalid_urls():
    # Non-allowlisted domain
    res = validate_url("https://malicious-site.com/fake-tender")
    assert res.is_valid is False
    assert "not in the allow-list" in res.error_message

    # Private IP / SSRF
    res = validate_url("https://127.0.0.1/secret-tender")
    assert res.is_valid is False
    assert "blocked" in res.error_message

    # Non-HTTP protocol
    res = validate_url("ftp://tenders.infralens.in/tender/123")
    assert res.is_valid is False
    assert "Invalid protocol" in res.error_message

    # Portal homepage without slug
    res = validate_url("https://tenders.infralens.in/")
    assert res.is_valid is False
    assert "homepage without a specific tender slug" in res.error_message


def test_valid_tender_numbers():
    cases = [
        ("GEM/2026/B/894210", "GeM Bid"),
        ("GEM/2025/R/1234567", "GeM Bid"),
        ("2026_ERDAElectr_320314_1", "CPPP / eProcure"),
        ("2026_WRD_503672_1", "CPPP / eProcure"),
        ("pind-2627-00220-320314", "Standard Tender Ref"),
    ]
    for t_num, expected_fmt in cases:
        res = validate_tender_number(t_num)
        assert res.is_valid is True, f"Expected {t_num} to be valid, got: {res.error_message}"
        assert res.input_type == "TENDER_NUMBER"
        assert res.tender_format == expected_fmt


def test_invalid_tender_numbers():
    invalid_cases = [
        "",
        "   ",
        "abc",  # too short (< 4 chars)
        "SELECT * FROM tenders",  # contains spaces / SQL injection attempt
        "<script>alert(1)</script>",  # invalid characters
    ]
    for t_num in invalid_cases:
        res = validate_tender_number(t_num)
        assert res.is_valid is False


def test_unified_identifier_validator():
    # Detects URL correctly
    url_res = validate_identifier("https://tenders.infralens.in/tender/test-1")
    assert url_res.is_valid is True
    assert url_res.input_type == "URL"

    # Detects Tender Number correctly
    tnum_res = validate_identifier("GEM/2026/B/894210")
    assert tnum_res.is_valid is True
    assert tnum_res.input_type == "TENDER_NUMBER"

    # Flags invalid inputs early
    bad_res = validate_identifier("invalid url or number with spaces")
    assert bad_res.is_valid is False
