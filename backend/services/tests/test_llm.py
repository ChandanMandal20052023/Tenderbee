"""
Tests for LLMAdapter, TenderNoticeExtraction schema, and anti-hallucination grounding gate.
"""
from unittest.mock import MagicMock
from pathlib import Path
import pytest

from backend.services.llm import (
    GroundedField,
    LLMAdapter,
    TenderNoticeExtraction,
)
from backend.engine.parser import TenderPDFExtractor, is_grounded
from backend.engine.schema import TenderPDFExtractionResult


def test_tender_notice_extraction_schema():
    """Verify TenderNoticeExtraction Pydantic model and JSON schema generation."""
    schema = TenderNoticeExtraction.model_json_schema()
    assert "properties" in schema
    assert "tender_number" in schema["properties"]
    assert "estimated_value_inr" in schema["properties"]
    assert "min_average_annual_turnover_inr" in schema["properties"]
    assert "mandatory_documents" in schema["properties"]


def test_llm_adapter_model_configuration(monkeypatch):
    """Verify LLMAdapter defaults to gemini-2.0-flash and respects GEMINI_MODEL env."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    adapter = LLMAdapter()
    assert adapter.model == "gemini-2.0-flash"
    assert adapter.api_key is None

    # Environment variable override
    monkeypatch.setenv("GEMINI_MODEL", "gemini-1.5-pro")
    adapter_custom = LLMAdapter()
    assert adapter_custom.model == "gemini-1.5-pro"


def test_llm_adapter_mock_mode_when_no_api_key(monkeypatch):
    """Verify LLMAdapter safely returns None when no API key is provided."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    adapter = LLMAdapter()
    result = adapter.extract_structured(
        pages=[(1, "Sample tender text")],
        instructions="Extract data",
        response_schema=TenderNoticeExtraction,
    )
    assert result is None


def test_tender_pdf_extractor_grounding_gate_accepts_valid_and_rejects_hallucinations(tmp_path):
    """
    Anti-Hallucination Gate Verification:
    - Grounded quotes are accepted and applied.
    - Hallucinated quotes (not physically on cited page) are rejected.
    """
    sample_pdf = Path(__file__).resolve().parents[3] / "samples" / "western_railway_mech_tpa_2026.pdf"
    assert sample_pdf.exists()

    # Create mock LLMAdapter that returns one grounded field and one hallucinated field
    mock_adapter = MagicMock()
    mock_adapter.api_key = "test_key"

    # Western Railway sample notice has "BCT-23-24-MECH-TPA-02" on page 1
    # and has financial criteria on page 4
    mock_extraction = TenderNoticeExtraction(
        tender_number=GroundedField(
            value="Mech-TPA-2026",
            page=1,
            quote="e-Tender Notice No: Mech-TPA-2026",
            confidence=1.0,
        ),
        tender_title=GroundedField(
            value="Contract work for provision of manpower for Train passing activities",
            page=1,
            quote="Name of Work: Contract work for provision of manpower for Train passing activities",
            confidence=1.0,
        ),
        buyer_name=GroundedField(
            value="WESTERN RAILWAY MUMBAI CENTRAL DIVISION",
            page=1,
            quote="WESTERN RAILWAY MUMBAI CENTRAL DIVISION",
            confidence=0.95,
        ),
        submission_deadline=GroundedField(
            value="2026-03-31T15:00:00Z",
            page=1,
            quote="TOP SHEET",
            confidence=0.9,
        ),
        # HALLUCINATED FIELD: quote that does NOT exist on page 1
        estimated_value_inr=GroundedField(
            value=9999999999.0,
            page=1,
            quote="This is an imaginary hallucinated clause that does not exist in Western Railway PDF",
            confidence=1.0,
        ),
        mandatory_documents=["udyam_certificate", "ca_turnover_certificate"],
    )
    mock_adapter.extract_structured.return_value = mock_extraction

    extractor = TenderPDFExtractor(llm_adapter=mock_adapter, use_llm=True)
    result: TenderPDFExtractionResult = extractor.extract_from_pdf(str(sample_pdf))

    # Grounded fields were applied
    assert result.tender_number == "Mech-TPA-2026"
    assert "WESTERN RAILWAY" in result.buyer_name
    assert "Contract work for provision of manpower" in result.tender_title

    # Hallucinated value was REJECTED by is_grounded gate!
    # It must NOT be 9999999999.0; instead it preserves the real estimated value
    assert result.estimated_value_inr != 9999999999.0
    assert result.estimated_value_inr == 522615823.34


def test_tender_schema_generation():
    """Verify TenderPDFExtractionResult emits standard OpenAPI-compliant JSON schema."""
    extractor = TenderPDFExtractor()
    data = extractor.get_json_schema()
    assert data["title"] == "TenderPDFExtractionResult"
    assert "properties" in data
    assert "tender_title" in data["properties"]
    assert "total_pages" in data["properties"]
    assert "verbatim_clauses" in data["properties"]
    assert "eligibility_rules" in data["properties"]
    assert "estimated_value_inr" in data["properties"]

