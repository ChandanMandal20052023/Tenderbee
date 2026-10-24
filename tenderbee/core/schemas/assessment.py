"""Assessment, Verdict, and Fix-list schemas."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from tenderbee.core.schemas.enums import (
    DocumentType,
    ReadinessState,
    ReasonCode,
    VerdictStatus,
)
from tenderbee.core.schemas.evidence import EvidenceItem


class Verdict(BaseModel):
    """The result of evaluating a single rule against extracted evidence."""
    rule_id: str = Field(..., description="The ID of the rule evaluated")
    result: VerdictStatus = Field(..., description="VERIFIED, VERIFIED_WITH_WARNING, NEEDS_REVIEW, REJECTED, WAIVED")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Minimum confidence among supporting evidence")
    reason_code: ReasonCode = Field(..., description="Canonical reason code explaining the verdict")
    evidence: List[EvidenceItem] = Field(default_factory=list, description="Supporting evidence with quotes and pages")
    next_action: str = Field(..., description="Clear human next action to resolve or verify")
    computed_value: Optional[Any] = Field(default=None, description="E.g. calculated turnover average in INR")


class MissingDocument(BaseModel):
    """Document mandated by tender rules that was not provided."""
    document_type: DocumentType = Field(..., description="Missing document type")
    mandatory: bool = Field(default=True)
    reason_code: ReasonCode = Field(default=ReasonCode.DOC_MISSING)
    next_action: str = Field(..., description="Action prompt for user")


class FixListItem(BaseModel):
    """Prioritized fix item for the bidder to reach READY state."""
    rank: int = Field(..., ge=1, description="Priority rank (1 = highest priority)")
    blocking: bool = Field(..., description="Whether this issue blocks the tender readiness")
    rule_id: str = Field(..., description="Rule ID requiring fix")
    reason_code: ReasonCode = Field(...)
    effort: str = Field(
        ...,
        description="Estimated effort: 're_upload' | 're_scan' | 'obtain_certificate' | 'obtain_new_registration'"
    )
    next_action: str = Field(...)


class RulePackMeta(BaseModel):
    """Version and hash of the rule pack evaluated against."""
    version: int
    content_hash: str


class AssessmentResponse(BaseModel):
    """The complete response returned by GET /api/v1/assessments/{id}/."""
    assessment_id: str = Field(...)
    rule_pack: RulePackMeta = Field(...)
    readiness_state: ReadinessState = Field(..., description="BLOCKED | REVIEW_REQUIRED | READY")
    readiness_score: int = Field(..., ge=0, le=100, description="Advisory score 0 to 100")
    disclaimer: str = Field(
        default="Decision support only. Not a guarantee of eligibility.",
        description="Mandatory legal disclaimer"
    )
    verdicts: List[Verdict] = Field(default_factory=list)
    missing_documents: List[MissingDocument] = Field(default_factory=list)
    fix_list: List[FixListItem] = Field(default_factory=list)
