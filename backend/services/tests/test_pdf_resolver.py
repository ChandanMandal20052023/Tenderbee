"""
Tests for TenderPDFResolver and PDF validation engine.
"""
import io
import os
import tempfile
import pytest
from pathlib import Path
from backend.services.pdf_resolver import TenderPDFResolver
from backend.engine.parser import TenderPDFExtractor

def test_generate_official_notice_pdf():
    resolver = TenderPDFResolver(tinyfish_api_key=None)
    tender = {
        "tender_id": "tnd_unit_test",
        "tender_number": "TEST/HAR/2026/001",
        "title": "Procurement of Medical Diagnostic Equipment",
        "state": "Haryana",
        "category": "Goods",
        "estimated_value_inr": 8000000.0,
        "emd_amount_inr": 160000.0,
        "tenure_months": 24,
    }

    pdf_bytes = resolver._generate_official_notice_pdf(tender)
    assert pdf_bytes is not None
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 2000

    # Verify that the generated PDF passes our validator
    assert resolver._is_valid_indian_tender_pdf("https://eprocure.gov.in/test.pdf", pdf_bytes, tender) is True

    # Parse with TenderPDFExtractor and ensure clauses are detected
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        extractor = TenderPDFExtractor()
        extraction = extractor.extract_from_pdf(tmp_path)
        assert extraction.tender_number == "TEST/HAR/2026/001"
        assert len(extraction.verbatim_clauses) >= 4
        # Check that turnover and liquidity clauses are identified
        types = {c.clause_type for c in extraction.verbatim_clauses}
        assert "turnover_requirement" in types
        assert "liquidity_requirement" in types
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_is_valid_indian_tender_pdf_rejections():
    resolver = TenderPDFResolver(tinyfish_api_key=None)
    dummy_tender = {"tender_number": "DUMMY/2026"}

    # 1. Empty or too small
    assert resolver._is_valid_indian_tender_pdf("http://example.com/test.pdf", b"", dummy_tender) is False
    assert resolver._is_valid_indian_tender_pdf("http://example.com/test.pdf", b"%PDF123", dummy_tender) is False

    # 2. Foreign TLDs
    fake_pdf = b"%PDF-1.4 " + b"tender notice procurement " * 100
    assert resolver._is_valid_indian_tender_pdf("https://tenders.go.ke/doc.pdf", fake_pdf, dummy_tender) is False
    assert resolver._is_valid_indian_tender_pdf("https://eproc.gov.pk/doc.pdf", fake_pdf, dummy_tender) is False
