"""Evidence and Grounding Schemas."""
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

from tenderbee.core.schemas.enums import ReasonCode

T = TypeVar("T")


class EvidenceItem(BaseModel):
    """Evidence attached to an assessment verdict."""
    page: int = Field(..., description="1-indexed page number in source document")
    quote: str = Field(..., description="Verbatim text quote from the document")
    source: str = Field(default="uploaded_document", description="Source of evidence")
    bounding_box: Optional[list[float]] = Field(
        default=None,
        description="Optional [x0, y0, x1, y1] normalized bounding box coordinates"
    )


class GroundedField(BaseModel, Generic[T]):
    """Every extracted field must carry evidence and grounding metadata."""
    value: T = Field(..., description="Parsed or typed value of the field")
    verbatim: str = Field(..., description="Exact string as it appears in document")
    page: int = Field(..., ge=1, description="1-indexed page number where quote is found")
    quote: str = Field(..., description="Verbatim quote surrounding the field on that page")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model-reported confidence (0.0 to 1.0)")
    grounded: bool = Field(default=True, description="Whether the quote was verified against page text")
    reason_code: Optional[ReasonCode] = Field(
        default=None,
        description="Reason code if grounding failed or warning attached"
    )
