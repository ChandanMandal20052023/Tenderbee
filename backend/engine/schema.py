"""
Pure-Python schema definitions for rules and compliance criteria.
Zero external framework dependencies (pure Pydantic + standard library).
"""
import io
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field

T = TypeVar("T")


# ==============================================================================
# ENUMS
# ==============================================================================

class VerdictStatus(str, Enum):
    """Overall assessment state for a bidder on a specific tender."""
    READY = "READY"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    BLOCKED = "BLOCKED"


class ReadinessState(str, Enum):
    """Readiness classification."""
    READY = "READY"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    BLOCKED = "BLOCKED"


class RuleType(str, Enum):
    """Types of deterministic compliance rules."""
    DOCUMENT_REQUIRED = "document_required"
    NUMERIC_THRESHOLD = "numeric_threshold"
    DATE_VALIDITY = "date_validity"
    FIELD_IN_SET = "field_in_set"
    IDENTIFIER_PRESENT = "identifier_present"
    SCHEMA_VALIDATION = "schema_validation"


class RuleStatus(str, Enum):
    """Lifecycle status of a RulePack."""
    DRAFT = "DRAFT"
    FROZEN = "FROZEN"
    ARCHIVED = "ARCHIVED"


class DocumentType(str, Enum):
    """Supported procurement compliance document types."""
    UDYAM_CERTIFICATE = "udyam_certificate"
    CA_TURNOVER_CERTIFICATE = "ca_turnover_certificate"
    NSIC_REGISTRATION = "nsic_registration"
    GST_CERTIFICATE = "gst_certificate"
    PAN_CARD = "pan_card"
    WORK_EXPERIENCE = "work_experience_certificate"
    BANKING_REFERENCE = "banking_reference_annexure_x"
    TRUTHFULNESS_UNDERTAKING = "truthfulness_undertaking_annexure_i"
    BID_FORM = "bid_form_annexure_ii"
    OTHER = "other"


class EnterpriseType(str, Enum):
    """MSME Enterprise Classification."""
    MICRO = "MICRO"
    SMALL = "SMALL"
    MEDIUM = "MEDIUM"


class TurnoverUnit(str, Enum):
    """Currency unit for financial turnover certificates."""
    LAKHS = "lakhs"
    CRORES = "crores"
    THOUSANDS = "thousands"
    RUPEES = "rupees"


class ReasonCode(str, Enum):
    """Reason code catalog for verdicts and fix-list items."""
    RULE_MET = "RULE_MET"
    THRESHOLD_NOT_MET = "THRESHOLD_NOT_MET"
    NUMERIC_THRESHOLD_FAILED = "NUMERIC_THRESHOLD_FAILED"
    DOCUMENT_MISSING = "DOCUMENT_MISSING"
    DOC_MISSING = "DOC_MISSING"
    DOCUMENT_EXPIRED = "DOCUMENT_EXPIRED"
    UNIT_AMBIGUOUS = "UNIT_AMBIGUOUS"
    UDIN_MISSING = "UDIN_MISSING"
    NIC_NOT_COVERED = "NIC_NOT_COVERED"
    INSUFFICIENT_YEARS = "INSUFFICIENT_YEARS"
    QUOTE_NOT_GROUNDED = "QUOTE_NOT_GROUNDED"
    UNGROUNDED_EVIDENCE = "UNGROUNDED_EVIDENCE"
    OCR_LOW_CONF = "OCR_LOW_CONF"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    EXTERNAL_UNAVAILABLE = "EXTERNAL_UNAVAILABLE"


# ==============================================================================
# EVIDENCE & GROUNDING
# ==============================================================================

class EvidenceItem(BaseModel):
    """Evidence attached to an assessment verdict."""
    page: int = Field(default=1, ge=1, description="1-indexed page number in source document")
    quote: str = Field(default="", description="Verbatim text quote from the document")
    source: str = Field(default="uploaded_document", description="Source of evidence")
    value: Optional[Any] = Field(default=None, description="Typed value extracted")
    is_grounded: bool = Field(default=True, description="Whether quote is grounded to page text")
    grounded: bool = Field(default=True, description="Grounding status alias")
    bounding_box: Optional[List[float]] = Field(default=None, description="Optional [x0, y0, x1, y1] normalized coords")


class GroundedField(BaseModel, Generic[T]):
    """Every extracted field must carry evidence and grounding metadata."""
    value: T = Field(..., description="Parsed or typed value of the field")
    verbatim: str = Field(..., description="Exact string as it appears in document")
    page: int = Field(..., ge=1, description="1-indexed page number where quote is found")
    quote: str = Field(..., description="Verbatim quote surrounding the field on that page")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model-reported confidence (0.0 to 1.0)")
    grounded: bool = Field(default=True, description="Whether the quote was verified against page text")
    reason_code: Optional[ReasonCode] = Field(default=None, description="Reason code if grounding failed")


# ==============================================================================
# OCR & COMMON EXTRACTION
# ==============================================================================

class OCRPageSummary(BaseModel):
    """OCR metrics per page."""
    page: int = Field(..., ge=1)
    ocr_confidence: float = Field(..., ge=0.0, le=1.0, description="1.0 for digital PDF layer")
    text_length: int = Field(..., ge=0)
    is_scanned: bool = Field(default=False)


class OCRSummary(BaseModel):
    """Summary of text layer and OCR quality across the document."""
    total_pages: int = Field(..., ge=1)
    min_page_confidence: float = Field(..., ge=0.0, le=1.0)
    average_confidence: float = Field(..., ge=0.0, le=1.0)
    pages: List[OCRPageSummary] = Field(default_factory=list)


class CommonDocumentExtraction(BaseModel):
    """Canonical unified extraction envelope."""
    document_id: str = Field(..., description="Unique document ID")
    document_type: DocumentType = Field(..., description="Document type")
    model: str = Field(default="gemini-2.5-flash", description="LLM model used for extraction")
    prompt_version: str = Field(default="1.0.0", description="Semantic prompt version")
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    fields: Dict[str, GroundedField[Any]] = Field(default_factory=dict)
    tables: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    ocr_summary: Optional[OCRSummary] = Field(default=None)
    grounding_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    all_grounded: bool = Field(default=True)


# ==============================================================================
# BIDDER DOCUMENT EXTRACTIONS
# ==============================================================================

class TurnoverRow(BaseModel):
    """Single Financial Year turnover row in CA certificate."""
    fy_label: str = Field(..., description="Raw label e.g. '2023-24' or 'FY 22-23'")
    fy_end_date: Optional[str] = Field(default=None, description="Canonical end date YYYY-MM-DD")
    amount_raw: str = Field(..., description="Verbatim amount string from certificate")
    amount_inr: Optional[float] = Field(default=None, description="Normalized amount in INR")
    page: int = Field(..., ge=1)
    quote: str = Field(..., description="Verbatim line or table row quote")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    grounded: bool = Field(default=True)


class UdyamExtraction(BaseModel):
    """Extracted fields from an Udyam Registration Certificate."""
    udyam_number: GroundedField[str] = Field(..., description="Udyam Registration Number e.g. UDYAM-MH-01-0012345")
    enterprise_name: GroundedField[str] = Field(..., description="Legal name of enterprise")
    enterprise_type: GroundedField[EnterpriseType] = Field(..., description="MICRO, SMALL, or MEDIUM")
    nic_codes: List[GroundedField[str]] = Field(default_factory=list, description="NIC activity codes")
    registration_date: Optional[GroundedField[str]] = Field(default=None)
    state: Optional[GroundedField[str]] = Field(default=None)
    pin_code: Optional[GroundedField[str]] = Field(default=None)


class CATurnoverExtraction(BaseModel):
    """Extracted fields from a Chartered Accountant Turnover Certificate."""
    ca_firm_name: GroundedField[str] = Field(..., description="Name of the CA firm")
    ca_firm_reg_number: Optional[GroundedField[str]] = Field(default=None)
    ca_membership_number: Optional[GroundedField[str]] = Field(default=None)
    udin: GroundedField[str] = Field(..., description="18-character ICAI UDIN")
    certificate_date: Optional[GroundedField[str]] = Field(default=None)
    unit_statement: GroundedField[TurnoverUnit] = Field(..., description="Turnover unit e.g. LAKHS, CRORES")
    turnover_rows: List[TurnoverRow] = Field(default_factory=list)
    stated_average: Optional[GroundedField[float]] = Field(default=None)


class NSICExtraction(BaseModel):
    """Extracted fields from an NSIC Registration Certificate."""
    nsic_number: GroundedField[str] = Field(..., description="NSIC registration number")
    enterprise_name: GroundedField[str] = Field(..., description="Enterprise name")
    store_details: List[GroundedField[str]] = Field(default_factory=list)
    valid_from: Optional[GroundedField[str]] = Field(default=None)
    valid_to: Optional[GroundedField[str]] = Field(default=None)


# ==============================================================================
# TENDER SPECIFICATIONS & PDF EXTRACTIONS
# ==============================================================================

class TenderClauseQuote(BaseModel):
    """Verbatim clause quote extracted with source page citation."""
    clause_type: str = Field(..., description="Requirement category e.g. turnover_requirement, udyam_requirement")
    page: int = Field(..., ge=1, description="1-indexed source PDF page number")
    quote: str = Field(..., description="Verbatim text sentence or clause from document")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class TenderPDFPage(BaseModel):
    """Page-level text metrics for extracted PDF."""
    page_number: int = Field(..., ge=1)
    text_snippet: str = Field(..., description="First 200 chars of page")
    char_count: int = Field(..., ge=0)
    is_scanned: bool = Field(default=False)


class TenderEligibilityRules(BaseModel):
    """Parsed numerical and categorical eligibility constraints."""
    min_annual_turnover_inr: Optional[float] = Field(default=None, description="Minimum required turnover in INR")
    turnover_years: int = Field(default=3, description="Number of financial years required")
    min_liquidity_inr: Optional[float] = Field(default=None, description="Minimum liquidity requirement in INR")
    min_work_experience_inr: Optional[float] = Field(default=None, description="Minimum single work contract in INR")
    udin_mandatory: bool = Field(default=False, description="Whether CA UDIN certification is mandatory")
    required_nic_prefixes: List[str] = Field(default_factory=list, description="Required MSME NIC prefixes")
    eligible_entity_types: List[str] = Field(default_factory=list, description="Eligible entity types (e.g. Railway PSUs)")


class TenderPDFExtractionResult(BaseModel):
    """
    Standard schema for Tender PDF extraction.
    Represents the complete structured understanding of a procurement notice.
    """
    tender_number: Optional[str] = Field(default=None, description="Official Tender/Bid Notice Number")
    tender_title: str = Field(..., description="Work Title / Scope of Contract")
    buyer_name: Optional[str] = Field(default=None, description="Procuring Authority / Railway Division")
    submission_deadline: Optional[str] = Field(default=None, description="Closing date/time")
    opening_date: Optional[str] = Field(default=None, description="Tender opening date/time")
    contract_period: Optional[str] = Field(default=None, description="Duration e.g. 4 Years / 48 Months")
    estimated_value_inr: Optional[float] = Field(default=None, description="Total advertised value in INR")
    emd_amount_inr: Optional[float] = Field(default=None, description="Earnest Money Deposit in INR")
    tender_fee_inr: Optional[float] = Field(default=None, description="Tender document fee in INR")
    processing_fee_inr: Optional[float] = Field(default=None, description="e-Procurement processing fee / bid submission fee in INR")
    dealing_officer: Optional[str] = Field(default=None, description="Dealing / Inviting Officer name and designation")
    org_hierarchy: List[str] = Field(default_factory=list, description="Department organizational hierarchy")
    mse_exemption_allowed: bool = Field(default=False, description="Whether MSME / MSE exemption from EMD applies")
    portal_website: Optional[str] = Field(default=None, description="e-Procurement portal URL (ireps.gov.in, eproc2.bihar.gov.in, gem.gov.in)")
    mandatory_documents: List[str] = Field(default_factory=list, description="List of required document identifiers")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Attached tender documents (NIT, BOQ, Corrigendum) with metadata")
    nit_attachment: Optional[Dict[str, Any]] = Field(default=None, description="Notice Inviting Tender attachment metadata")
    boq_attachment: Optional[Dict[str, Any]] = Field(default=None, description="Bill of Quantities attachment metadata")
    preview_details: Optional[Dict[str, Any]] = Field(default=None, description="Raw structured preview map from portal action modal")
    eligibility_rules: TenderEligibilityRules = Field(default_factory=TenderEligibilityRules)
    verbatim_clauses: List[TenderClauseQuote] = Field(default_factory=list, description="Verbatim clauses with page citations")
    total_pages: int = Field(..., ge=1, description="Total pages in the source PDF")
    digital_text_coverage: float = Field(default=1.0, ge=0.0, le=1.0, description="Ratio of pages with digital text")
    pages: List[TenderPDFPage] = Field(default_factory=list)

    @classmethod
    def get_json_schema(cls) -> dict:
        return cls.model_json_schema()


# ==============================================================================
# RULE PACKS
# ==============================================================================

class RuleSource(BaseModel):
    """Verbatim ground truth quote and page reference from tender notice."""
    page: int = Field(..., ge=1)
    quote: str = Field(..., description="Verbatim clause text from tender document")


class Rule(BaseModel):
    """Single compliance rule within a RulePack."""
    rule_id: str = Field(..., description="Canonical ID e.g. 'R-DOC-UDYAM', 'R-TURNOVER-AVG3'")
    type: Optional[RuleType] = Field(default=None, description="Deterministic evaluation rule type")
    rule_type: Optional[RuleType] = Field(default=None, description="Alternative field for rule type")
    document_type: Optional[Union[DocumentType, str]] = Field(default=None, description="Target document type")
    description: Optional[str] = Field(default=None, description="Human readable description")
    mandatory: bool = Field(default=True)
    params: Dict[str, Any] = Field(default_factory=dict)
    source: RuleSource = Field(..., description="Verbatim clause from tender document")
    field: Optional[str] = Field(default=None, description="Field name in document")
    operator: Optional[str] = Field(default=None, description="Operator: eq, gte, in, present")
    value: Optional[Any] = Field(default=None, description="Expected value or threshold")
    flags: List[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if self.type is None and self.rule_type is not None:
            self.type = self.rule_type
        elif self.rule_type is None and self.type is not None:
            self.rule_type = self.type


class ReferenceDates(BaseModel):
    """Key reference dates for time-sensitive compliance evaluation."""
    submission_deadline: datetime = Field(..., description="Tender closing deadline")
    bid_opening: Optional[datetime] = Field(default=None)


class RulePack(BaseModel):
    """Immutable, versioned collection of rules governing a tender."""
    tender_id: str = Field(...)
    version: int = Field(default=1, ge=1)
    status: RuleStatus = Field(default=RuleStatus.DRAFT)
    content_hash: str = Field(...)
    confirmed_by: Optional[str] = Field(default=None)
    confirmed_at: Optional[datetime] = Field(default=None)
    reference_dates: ReferenceDates = Field(...)
    rules: List[Rule] = Field(default_factory=list)


class TenderRuleDraftItem(BaseModel):
    """Single proposed compliance rule during tender intake."""
    rule_id: str
    type: RuleType
    mandatory: bool = True
    params: Dict[str, Any] = Field(default_factory=dict)
    verbatim_quote: str
    source_page: int = 1
    confidence: float = 1.0


class TenderRulePackDraft(BaseModel):
    """Initial LLM-proposed rule pack before human review."""
    tender_id: str
    tender_number: str
    tender_title: str
    buyer_name: Optional[str] = None
    submission_deadline: datetime
    proposed_rules: List[TenderRuleDraftItem]
    rationale: str


# ==============================================================================
# ASSESSMENT & VERDICTS
# ==============================================================================

class Verdict(BaseModel):
    """The result of evaluating a single rule against extracted evidence."""
    rule_id: str = Field(..., description="The ID of the rule evaluated")
    status: VerdictStatus = Field(..., description="Verdict status: READY, NEEDS_REVIEW, BLOCKED")
    reason_code: Optional[ReasonCode] = Field(default=None, description="Reason code explaining the verdict")
    message: Optional[str] = Field(default=None, description="Human explanation of verdict")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Supporting evidence quotes")
    computed_value: Optional[Any] = Field(default=None, description="Calculated value or metric")


class MissingDocument(BaseModel):
    """Document mandated by tender rules that was not provided."""
    document_type: Union[DocumentType, str] = Field(..., description="Missing document type")
    rule_id: str = Field(..., description="Mandating rule ID")
    description: str = Field(default="", description="Prompt for user")
    mandatory: bool = Field(default=True)


class FixListItem(BaseModel):
    """Prioritized fix item for the bidder to reach READY state."""
    rule_id: str = Field(..., description="Rule ID requiring fix")
    severity: str = Field(default="BLOCKING", description="'BLOCKING' or 'WARNING'")
    description: str = Field(..., description="Description of non-compliance")
    suggested_action: str = Field(..., description="Recommended remediation step")
    action_required: Optional[str] = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        if self.action_required is None:
            self.action_required = self.suggested_action


class RulePackMeta(BaseModel):
    """Version and hash metadata of the rule pack evaluated against."""
    rule_pack_id: str = Field(default="")
    version: int = Field(default=1)
    status: str = Field(default="DRAFT")
    content_hash: Optional[str] = Field(default=None)
    confirmed_by: Optional[str] = Field(default=None)
    confirmed_at: Optional[datetime] = Field(default=None)


class AssessmentResponse(BaseModel):
    """Complete evaluation outcome emitted by ComplianceEngine."""
    readiness: ReadinessState = Field(..., description="READY, NEEDS_REVIEW, BLOCKED")
    verdicts: List[Verdict] = Field(default_factory=list)
    missing_documents: List[MissingDocument] = Field(default_factory=list)
    fix_list: List[FixListItem] = Field(default_factory=list)
    rule_pack_meta: RulePackMeta
    assessment_id: Optional[str] = Field(default=None)
    organization_id: Optional[str] = Field(default="org_default")

    @property
    def overall_status(self) -> VerdictStatus:
        if self.readiness == ReadinessState.BLOCKED:
            return VerdictStatus.BLOCKED
        elif self.readiness == ReadinessState.NEEDS_REVIEW:
            return VerdictStatus.NEEDS_REVIEW
        return VerdictStatus.READY

