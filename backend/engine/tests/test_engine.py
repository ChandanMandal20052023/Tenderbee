"""
Unit and regression tests for backend.engine deterministic rules engine and parser.
Pure-Python test suite running completely independent of external databases or web services.
"""
import json
from pathlib import Path
import pytest

from backend.engine.checks import ComplianceEngine
from backend.engine.parser import TenderPDFExtractor, is_grounded, norm
from backend.engine.schema import (
    DocumentType,
    EvidenceItem,
    ReasonCode,
    RulePack,
    VerdictStatus,
)

GOLDEN_RULES_FILE = Path(__file__).resolve().parents[2] / "golden" / "cases" / "rules.json"
SAMPLE_PDF = Path(__file__).resolve().parents[3] / "samples" / "western_railway_mech_tpa_2026.pdf"


# ==============================================================================
# 1. NORMALIZATION & GROUNDING TESTS
# ==============================================================================

def test_text_normalization():
    """Verifies that norm() standardizes unicode dashes, case, and whitespace."""
    raw = "  Minimum \u2013 150%  of   Advertised \u2014 Value: Rs.  78,39,23,735.01  "
    normalized = norm(raw)
    assert normalized == "minimum - 150% of advertised - value: rs. 78,39,23,735.01"


def test_is_grounded_exact_and_fuzzy():
    """Verifies is_grounded returns True for exact and minor OCR variance substrings."""
    page_text = """
    WESTERN RAILWAY
    Tender Notice No: Mech-TPA-2026
    The contractor shall submit a certificate from Chartered Accountant with UDIN.
    Turnover Requirement (T-1): 150% of the Advertised Value i.e. Rs. 78,39,23,735.01.
    """
    # Exact quote
    assert is_grounded("150% of the Advertised Value i.e. Rs. 78,39,23,735.01", page_text)

    # Normalized whitespace & case
    assert is_grounded("150%  of  the  advertised value", page_text)

    # Non-existent quote
    assert not is_grounded("Minimum turnover of Rs. 100 Crore", page_text)


# ==============================================================================
# 2. GOLDEN RULE PACK DESERIALIZATION
# ==============================================================================

def test_load_golden_rule_pack():
    """Verifies that the golden rule pack fixture is valid and conforms to RulePack schema."""
    assert GOLDEN_RULES_FILE.exists(), f"Missing golden rules file: {GOLDEN_RULES_FILE}"
    with open(GOLDEN_RULES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    rule_pack = RulePack(**data)
    assert rule_pack.tender_id == "tnd_mech_tpa_2026"
    assert rule_pack.status.value == "FROZEN"
    assert len(rule_pack.rules) == 8

    rule_ids = [r.rule_id for r in rule_pack.rules]
    assert "R-DOC-UDYAM" in rule_ids
    assert "R-TURNOVER-AVG3" in rule_ids
    assert "R-UDIN" in rule_ids
    assert "R-LIQUIDITY" in rule_ids
    assert "R-WORK-EXP" in rule_ids
    assert "R-ENTITY-ELIGIBILITY" in rule_ids


# ==============================================================================
# 3. DETERMINISTIC ENGINE EVALUATION TESTS
# ==============================================================================

@pytest.fixture
def golden_rule_pack() -> RulePack:
    with open(GOLDEN_RULES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return RulePack(**data)


@pytest.fixture
def compliance_engine() -> ComplianceEngine:
    return ComplianceEngine()


def test_engine_eval_fully_qualified_bidder(compliance_engine, golden_rule_pack):
    """Verifies that a fully qualified PSU bidder receives VerdictStatus.READY."""
    bidder_documents = {
        DocumentType.UDYAM_CERTIFICATE.value: {
            "status": EvidenceItem(
                value="ACTIVE",
                page=1,
                quote="Udyam Certificate Status: ACTIVE",
                is_grounded=True,
            ),
            "entity_type": EvidenceItem(
                value="Railway PSUs",
                page=1,
                quote="Category: Railway PSUs",
                is_grounded=True,
            ),
        },
        DocumentType.CA_TURNOVER_CERTIFICATE.value: {
            "status": EvidenceItem(
                value="SUBMITTED",
                page=1,
                quote="CA Certificate Submitted",
                is_grounded=True,
            ),
            "average_turnover_inr": EvidenceItem(
                value=850000000.00,  # 85 Cr > 78.39 Cr
                page=2,
                quote="Average Annual Turnover: Rs. 85,00,00,000.00",
                is_grounded=True,
            ),
            "udin": EvidenceItem(
                value="26012345ABCDEF1234",
                page=2,
                quote="UDIN: 26012345ABCDEF1234",
                is_grounded=True,
            ),
        },
        DocumentType.BANKING_REFERENCE.value: {
            "available_credit_facility_inr": EvidenceItem(
                value=30000000.00,  # 3 Cr > 2.61 Cr
                page=1,
                quote="Approved overdraft limit: Rs. 3,00,00,000.00",
                is_grounded=True,
            ),
        },
        DocumentType.WORK_EXPERIENCE.value: {
            "contract_value_inr": EvidenceItem(
                value=200000000.00,  # 20 Cr > 18.29 Cr
                page=1,
                quote="Completed Contract Value: Rs. 20,00,00,000.00",
                is_grounded=True,
            ),
        },
        DocumentType.TRUTHFULNESS_UNDERTAKING.value: {
            "signed": EvidenceItem(
                value=True,
                page=1,
                quote="Signed by Managing Director",
                is_grounded=True,
            ),
        },
    }

    result = compliance_engine.evaluate(golden_rule_pack, bidder_documents)

    assert result.overall_status == VerdictStatus.READY
    assert len(result.missing_documents) == 0
    assert len(result.fix_list) == 0
    assert all(v.status == VerdictStatus.READY for v in result.verdicts)


def test_engine_eval_missing_required_document(compliance_engine, golden_rule_pack):
    """Verifies that missing Udyam certificate produces BLOCKED verdict with missing_documents record."""
    # Completely omit Udyam certificate
    bidder_documents = {
        DocumentType.CA_TURNOVER_CERTIFICATE.value: {
            "status": EvidenceItem(value="SUBMITTED", page=1, quote="Submitted", is_grounded=True),
            "average_turnover_inr": EvidenceItem(value=900000000.0, page=2, quote="90 Cr", is_grounded=True),
            "udin": EvidenceItem(value="UDIN123", page=2, quote="UDIN123", is_grounded=True),
        },
    }

    result = compliance_engine.evaluate(golden_rule_pack, bidder_documents)

    assert result.overall_status == VerdictStatus.BLOCKED
    assert len(result.missing_documents) >= 1
    missing_types = [d.document_type for d in result.missing_documents]
    assert DocumentType.UDYAM_CERTIFICATE in missing_types


def test_engine_eval_failing_numeric_threshold(compliance_engine, golden_rule_pack):
    """Verifies that lower turnover produces BLOCKED verdict with actionable fix item."""
    bidder_documents = {
        DocumentType.UDYAM_CERTIFICATE.value: {
            "status": EvidenceItem(value="ACTIVE", page=1, quote="ACTIVE", is_grounded=True),
            "entity_type": EvidenceItem(value="Railway PSUs", page=1, quote="Railway PSUs", is_grounded=True),
        },
        DocumentType.CA_TURNOVER_CERTIFICATE.value: {
            "status": EvidenceItem(value="SUBMITTED", page=1, quote="Submitted", is_grounded=True),
            # Turnover: 50 Cr < 78.39 Cr required
            "average_turnover_inr": EvidenceItem(
                value=500000000.00,
                page=2,
                quote="Average Annual Turnover: Rs. 50,00,00,000.00",
                is_grounded=True,
            ),
            "udin": EvidenceItem(value="UDIN123456", page=2, quote="UDIN123456", is_grounded=True),
        },
        DocumentType.BANKING_REFERENCE.value: {
            "available_credit_facility_inr": EvidenceItem(value=30000000.00, page=1, quote="3 Cr", is_grounded=True),
        },
        DocumentType.WORK_EXPERIENCE.value: {
            "contract_value_inr": EvidenceItem(value=200000000.00, page=1, quote="20 Cr", is_grounded=True),
        },
        DocumentType.TRUTHFULNESS_UNDERTAKING.value: {
            "signed": EvidenceItem(value=True, page=1, quote="Signed", is_grounded=True),
        },
    }

    result = compliance_engine.evaluate(golden_rule_pack, bidder_documents)

    assert result.overall_status == VerdictStatus.BLOCKED
    turnover_verdict = next(v for v in result.verdicts if v.rule_id == "R-TURNOVER-AVG3")
    assert turnover_verdict.status == VerdictStatus.BLOCKED
    assert turnover_verdict.reason_code == ReasonCode.NUMERIC_THRESHOLD_FAILED

    # Check actionable fix list
    assert len(result.fix_list) >= 1
    turnover_fix = next(f for f in result.fix_list if f.rule_id == "R-TURNOVER-AVG3")
    assert "783,923,735.01" in turnover_fix.action_required or "78,39,23,735.01" in turnover_fix.action_required


def test_engine_eval_ungrounded_evidence_triggers_review(compliance_engine, golden_rule_pack):
    """Critical safety invariant: ungrounded evidence must never pass silently."""
    bidder_documents = {
        DocumentType.UDYAM_CERTIFICATE.value: {
            "status": EvidenceItem(value="ACTIVE", page=1, quote="ACTIVE", is_grounded=True),
            "entity_type": EvidenceItem(value="Railway PSUs", page=1, quote="Railway PSUs", is_grounded=True),
        },
        DocumentType.CA_TURNOVER_CERTIFICATE.value: {
            "status": EvidenceItem(value="SUBMITTED", page=1, quote="Submitted", is_grounded=True),
            # High turnover, but is_grounded is False (hallucination or unverified OCR)
            "average_turnover_inr": EvidenceItem(
                value=900000000.00,
                page=2,
                quote="Unverified quote",
                is_grounded=False,
            ),
            "udin": EvidenceItem(value="UDIN123456", page=2, quote="UDIN123456", is_grounded=True),
        },
        DocumentType.BANKING_REFERENCE.value: {
            "available_credit_facility_inr": EvidenceItem(value=30000000.00, page=1, quote="3 Cr", is_grounded=True),
        },
        DocumentType.WORK_EXPERIENCE.value: {
            "contract_value_inr": EvidenceItem(value=200000000.00, page=1, quote="20 Cr", is_grounded=True),
        },
        DocumentType.TRUTHFULNESS_UNDERTAKING.value: {
            "signed": EvidenceItem(value=True, page=1, quote="Signed", is_grounded=True),
        },
    }

    result = compliance_engine.evaluate(golden_rule_pack, bidder_documents)

    turnover_verdict = next(v for v in result.verdicts if v.rule_id == "R-TURNOVER-AVG3")
    assert turnover_verdict.status == VerdictStatus.NEEDS_REVIEW
    assert turnover_verdict.reason_code == ReasonCode.UNGROUNDED_EVIDENCE


# ==============================================================================
# 4. PDF EXTRACTOR INTEGRATION TESTS
# ==============================================================================

def test_pdf_extractor_western_railway():
    """Verifies TenderPDFExtractor against the 86-page Western Railway sample notice."""
    if not SAMPLE_PDF.exists():
        pytest.skip(f"Sample PDF not found at {SAMPLE_PDF}")

    extractor = TenderPDFExtractor()
    extraction = extractor.extract_from_pdf(SAMPLE_PDF)

    assert extraction.tender_number == "Mech-TPA-2026"
    assert extraction.total_pages == 86
    assert extraction.estimated_value_inr == 522615823.34
    assert extraction.eligibility_rules.min_annual_turnover_inr == 783923735.01
    assert extraction.eligibility_rules.min_liquidity_inr == 26130791.17
    assert extraction.eligibility_rules.min_work_experience_inr == 182915538.17
    assert extraction.eligibility_rules.udin_mandatory is True
    assert "Railway PSUs" in extraction.eligibility_rules.eligible_entity_types

    # Verify JSON Schema output
    schema = extraction.get_json_schema()
    assert schema["type"] == "object"
    assert "tender_number" in schema["properties"]
