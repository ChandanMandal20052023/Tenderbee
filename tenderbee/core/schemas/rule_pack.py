"""Rule pack and rule specification schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from tenderbee.core.schemas.enums import RuleStatus, RuleType


class RuleSource(BaseModel):
    """Source reference inside the tender notice/document."""
    page: int = Field(..., ge=1, description="1-indexed page in the tender PDF")
    quote: str = Field(..., description="Verbatim clause text from the tender")


class Rule(BaseModel):
    """A single deterministic rule in a rule pack."""
    rule_id: str = Field(..., description="Unique rule identifier, e.g. R-TURNOVER-AVG3")
    type: RuleType = Field(..., description="Rule type from whitelisted enum")
    mandatory: bool = Field(default=True, description="Whether failure of this rule blocks readiness")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters specific to the rule type")
    source: RuleSource = Field(..., description="Tender clause page and quote")
    flags: List[str] = Field(default_factory=list, description="Advisory flags, e.g. ['AMBIGUOUS']")


class ReferenceDates(BaseModel):
    """Key reference dates for a tender."""
    submission_deadline: datetime = Field(..., description="Bid submission deadline (IST timezone-aware)")
    bid_opening: Optional[datetime] = Field(default=None, description="Bid opening date (IST timezone-aware)")


class RulePack(BaseModel):
    """A frozen or draft contract of requirements for a specific tender."""
    tender_id: str = Field(..., description="ID of the tender")
    version: int = Field(default=1, ge=1, description="Rule pack version")
    status: RuleStatus = Field(default=RuleStatus.DRAFT, description="DRAFT | IN_REVIEW | CONFIRMED | FROZEN")
    content_hash: Optional[str] = Field(default=None, description="SHA-256 hash of the canonical rules")
    confirmed_by: Optional[str] = Field(default=None, description="User ID who confirmed/froze the pack")
    confirmed_at: Optional[datetime] = Field(default=None, description="Timestamp of confirmation")
    reference_dates: ReferenceDates = Field(..., description="Tender reference dates")
    rules: List[Rule] = Field(default_factory=list, description="List of rules")


class TenderRuleDraftItem(BaseModel):
    """Rule candidate proposed by the LLM during tender intake."""
    rule_id: str = Field(..., description="Proposed rule ID, e.g. R-TURNOVER-AVG3")
    type: RuleType = Field(..., description="Rule type")
    mandatory: bool = Field(default=True)
    params: Dict[str, Any] = Field(..., description="Proposed parameters (threshold_inr, nic_codes, etc.)")
    source: RuleSource = Field(..., description="Page and verbatim quote from tender text")
    ambiguous: bool = Field(default=False, description="Whether clause wording is ambiguous")
    ambiguity_reason: Optional[str] = Field(default=None, description="Explanation if marked ambiguous")


class TenderRulePackDraft(BaseModel):
    """Output schema for LLM when analyzing tender documents."""
    tender_title: Optional[str] = Field(default=None)
    buyer_name: Optional[str] = Field(default=None)
    submission_deadline_iso: Optional[str] = Field(default=None, description="Extracted deadline in ISO format")
    bid_opening_iso: Optional[str] = Field(default=None, description="Extracted opening date in ISO format")
    proposed_rules: List[TenderRuleDraftItem] = Field(default_factory=list)
