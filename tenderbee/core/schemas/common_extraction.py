"""Unified common schema for extracted document data across all document types."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from tenderbee.core.schemas.enums import DocumentType
from tenderbee.core.schemas.evidence import GroundedField


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
    """
    The canonical unified extraction envelope.
    Stored in DocumentExtraction.fields JSON in the database, returned by
    GET /api/v1/documents/{id}/extraction/, and consumed by the Frontend
    Evidence Viewer and Quote Grounding Engine.
    """
    document_id: str = Field(..., description="Unique document ID")
    document_type: DocumentType = Field(..., description="Document type")
    model: str = Field(default="gemini-2.5-flash", description="LLM model used for extraction")
    prompt_version: str = Field(default="1.0.0", description="Semantic prompt version")
    extracted_at: datetime = Field(default_factory=datetime.utcnow)

    # Universal flat map of all extracted fields: field_name -> GroundedField
    # Enables the Frontend Evidence Viewer to inspect and highlight any field generically
    fields: Dict[str, GroundedField[Any]] = Field(
        default_factory=dict,
        description="Dictionary mapping field names to GroundedField objects"
    )

    # Optional structured tables (e.g. turnover_rows for CA certificates)
    tables: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Structured table rows such as turnover rows"
    )

    # OCR and grounding quality rollup
    ocr_summary: Optional[OCRSummary] = Field(default=None)
    grounding_rate: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Ratio of fields verified against page text"
    )
    all_grounded: bool = Field(
        default=True,
        description="True if every extracted field passed quote grounding"
    )
    is_usable: bool = Field(
        default=True,
        description="False if confidence < 0.60 or ungrounded blocking fields exist"
    )

    def get_field(self, name: str) -> Optional[GroundedField[Any]]:
        """Convenience accessor for a grounded field."""
        return self.fields.get(name)

    def ungrounded_fields(self) -> List[str]:
        """Returns names of all fields that failed quote grounding."""
        return [k for k, v in self.fields.items() if not v.grounded]
