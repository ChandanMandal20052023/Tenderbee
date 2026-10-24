"""
Structured LLM adapter, anti-hallucination XML prompt templates, and Pydantic schemas.
"""
import json
import logging
import os
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ==============================================================================
# SCHEMAS FOR BIDDER DOCUMENT EXTRACTIONS
# ==============================================================================

class GroundedField(BaseModel, Generic[T]):
    """Extracted field value strictly grounded with verbatim quote and page citation."""
    value: Optional[T] = Field(default=None, description="Extracted typed value or None if not found.")
    page: int = Field(default=1, ge=1, description="1-indexed source document page.")
    quote: str = Field(default="", description="Verbatim text quote from the page verifying this value.")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Extraction certainty score.")


class FinancialYearTurnover(BaseModel):
    financial_year: str = Field(..., description="E.g. '2022-2023' or '2023-2024'")
    turnover_inr: float = Field(..., description="Annual turnover in Indian Rupees (INR)")
    page: int = Field(default=1, ge=1)
    quote: str = Field(default="")


class UdyamCertificateExtraction(BaseModel):
    """Structured extraction schema for Ministry of MSME Udyam Registration Certificate."""
    enterprise_name: GroundedField[str]
    udyam_registration_number: GroundedField[str]
    enterprise_type: GroundedField[str]  # "MICRO", "SMALL", "MEDIUM"
    major_activity: GroundedField[str]   # "SERVICES", "MANUFACTURING"
    organization_type: Optional[GroundedField[str]] = None
    nic_2_digit_codes: List[str] = Field(default_factory=list)


class CATurnoverCertificateExtraction(BaseModel):
    """Structured extraction schema for Chartered Accountant Turnover Certificate & Balance Sheet."""
    ca_firm_name: GroundedField[str]
    ca_membership_number: GroundedField[str]
    udin: GroundedField[str]
    udin_date: Optional[GroundedField[str]] = None
    annual_turnovers: List[FinancialYearTurnover] = Field(default_factory=list)
    average_turnover_inr: GroundedField[float]


class NSICRegistrationExtraction(BaseModel):
    """Structured extraction schema for NSIC Government Purchase Enlistment Certificate."""
    store_name: GroundedField[str]
    certificate_number: GroundedField[str]
    monetary_limit_inr: GroundedField[float]
    valid_until: GroundedField[str]


class TruthfulnessUndertakingExtraction(BaseModel):
    """Structured extraction schema for Annexure-I Truthfulness & Non-Debarment Undertaking."""
    bidder_name: GroundedField[str]
    signatory_name: GroundedField[str]
    signatory_designation: GroundedField[str]
    is_signed: GroundedField[bool]
    non_debarment_confirmed: GroundedField[bool]
    date_signed: Optional[GroundedField[str]] = None


# ==============================================================================
# PROMPT TEMPLATES (ANTI-HALLUCINATION XML)
# ==============================================================================

SYSTEM_PROMPT_EXTRACTION = """You are an expert Indian Government Public Procurement Compliance Auditor.
Your task is to extract factual compliance criteria and bidder verification details from official documents.

CRITICAL GROUNDING RULES:
1. NEVER assume, extrapolate, or hallucinate any value.
2. Every extracted field MUST be grounded by:
   - 'page': the exact 1-indexed page number where the text physically appears.
   - 'quote': an exact verbatim substring from that page (including punctuation and numbers).
3. If an attribute or requirement is not explicitly stated in the document, return null/empty.
4. Output MUST conform strictly to the requested JSON Schema without conversational filler or Markdown wrapping.
"""

def build_document_prompt(pages: List[Tuple[int, str]], instructions: str) -> str:
    """Wraps document pages in structured XML tags to guarantee page grounding."""
    doc_content = []
    for page_num, text in pages:
        doc_content.append(f'<document_content page="{page_num}">\n{text.strip()}\n</document_content>')
    pages_xml = "\n\n".join(doc_content)
    return f"""{instructions}

DOCUMENT CONTENT:
{pages_xml}

Return ONLY the valid JSON object conforming strictly to the requested schema.
"""


# ==============================================================================
# PROVIDER-AGNOSTIC LLM ADAPTER
# ==============================================================================

M = TypeVar("M", bound=BaseModel)

class LLMAdapter:
    """
    Provider-agnostic adapter for extracting grounded structured data from documents.
    Supports Google Gemini API with JSON schema enforcement.
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model

    def extract_structured(
        self,
        pages: List[Tuple[int, str]],
        instructions: str,
        response_schema: Type[M],
    ) -> Optional[M]:
        prompt = build_document_prompt(pages, instructions)
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY provided. Structured LLM adapter running in mock mode.")
            return None

        try:
            import httpx
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT_EXTRACTION}]},
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "response_schema": response_schema.model_json_schema(),
                    "temperature": 0.0,
                },
            }
            resp = httpx.post(url, json=payload, timeout=60.0)
            if resp.status_code != 200:
                logger.error(f"Gemini API returned status {resp.status_code}: {resp.text}")
                return None

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return None

            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
            return response_schema.model_validate_json(raw_text)
        except Exception as e:
            logger.error(f"Failed to execute LLM extraction: {e}")
            return None
