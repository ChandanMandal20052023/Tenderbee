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


class TenderNoticeExtraction(BaseModel):
    """Structured extraction schema for official Government Tender Notice / NIT document."""
    tender_number: GroundedField[str]
    tender_title: GroundedField[str]
    buyer_name: GroundedField[str]
    submission_deadline: GroundedField[str]
    opening_date: Optional[GroundedField[str]] = None
    contract_period: Optional[GroundedField[str]] = None
    estimated_value_inr: Optional[GroundedField[float]] = None
    emd_amount_inr: Optional[GroundedField[float]] = None
    mse_exemption_allowed: Optional[GroundedField[bool]] = None
    min_average_annual_turnover_inr: Optional[GroundedField[float]] = None
    min_work_experience_inr: Optional[GroundedField[float]] = None
    min_liquidity_inr: Optional[GroundedField[float]] = None
    udin_mandatory: Optional[GroundedField[bool]] = None
    mandatory_documents: List[str] = Field(default_factory=list)


class ParsedSearchQuery(BaseModel):
    """Structured search criteria extracted from natural language prompt by LLM."""
    query: Optional[str] = Field(default=None, description="Residual keywords or project item terms (e.g. 'smart meter', 'cleaning', 'flyover'). DO NOT include state names, categories, or numbers extracted into dedicated fields.")
    state: Optional[str] = Field(default=None, description="Full official Indian State or Union Territory name (e.g. 'Uttar Pradesh', 'Rajasthan', 'Haryana', 'Bihar', 'Maharashtra'). If user types abbreviations like 'up' or 'rj', map to 'Uttar Pradesh' or 'Rajasthan'.")
    city_or_district: Optional[str] = Field(default=None, description="Specific city, town, or district e.g. 'Lucknow', 'Jaipur', 'Patna', 'Faridabad', 'Noida'")
    category: Optional[str] = Field(default=None, description="Procurement category: strictly 'Services', 'Works', or 'Goods'")
    min_value_inr: Optional[float] = Field(default=None, description="Minimum estimated contract value in INR (e.g. 5 Cr -> 50000000.0, 50 Lakh -> 5000000.0)")
    max_value_inr: Optional[float] = Field(default=None, description="Maximum estimated contract value in INR")
    min_tenure_months: Optional[int] = Field(default=None, description="Minimum contract tenure/duration in months (e.g. 2 years -> 24, 6 months -> 6)")
    buyer_name: Optional[str] = Field(default=None, description="Issuing organization or department name if mentioned e.g. 'UPPCL', 'Western Railway'")


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
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    def _clean_schema_for_gemini(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Inlines $defs/$ref for Gemini REST API compatibility."""
        defs = schema.get("$defs", {})
        def _resolve(node):
            if isinstance(node, dict):
                if "$ref" in node:
                    ref_key = node["$ref"].split("/")[-1]
                    if ref_key in defs:
                        return _resolve(defs[ref_key].copy())
                return {k: _resolve(v) for k, v in node.items() if k != "$defs"}
            elif isinstance(node, list):
                return [_resolve(item) for item in node]
            return node
        return _resolve(schema)

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
            cleaned_schema = self._clean_schema_for_gemini(response_schema.model_json_schema())
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "system_instruction": {"parts": [{"text": SYSTEM_PROMPT_EXTRACTION}]},
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "response_schema": cleaned_schema,
                    "temperature": 0.0,
                },
            }
            resp = httpx.post(url, json=payload, timeout=60.0)
            if resp.status_code == 404 and "gemini-2.0-flash" in self.model:
                fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                resp = httpx.post(fallback_url, json=payload, timeout=60.0)

            if resp.status_code != 200:
                logger.debug("Gemini API returned status %s: %s", resp.status_code, resp.text)
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

    def parse_query(self, query_text: str) -> Optional[ParsedSearchQuery]:
        """
        Uses LLM to parse natural language search queries into structured filters.
        """
        if not self.api_key:
            return None

        system_instruction = (
            "You are an expert Indian Government Public Procurement search parser. "
            "Analyze the user's search query and map it strictly to the structured schema: "
            "1. Location: If the user enters a state or territory (e.g. 'uttar pradesh', 'up', 'rajasthan', 'bihar', 'haryana', 'maharashtra'), "
            "set 'state' to the full title-case state name (e.g. 'Uttar Pradesh', 'Rajasthan') and leave 'query' as null unless extra search terms exist. "
            "2. Cities: If a city like 'lucknow', 'jaipur', 'patna', 'noida' is specified, populate 'city_or_district' and infer 'state'. "
            "3. Category: If services/cleaning/manpower/security is requested, set 'category' to 'Services'. "
            "If construction/civil/road/expressway/bridge, set 'category' to 'Works'. If supply/goods/equipment, set 'category' to 'Goods'. "
            "4. Numbers: Convert 'Cr' or 'Crores' (x 10,000,000) and 'Lakhs' (x 100,000) to numeric INR. "
            "5. Residual Keywords: Strip out all location names, categories, and numbers from 'query'. If only filters were given (e.g. 'services tender in uttar pradesh'), 'query' MUST be null."
        )

        try:
            import httpx
            cleaned_schema = self._clean_schema_for_gemini(ParsedSearchQuery.model_json_schema())
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "system_instruction": {"parts": [{"text": system_instruction}]},
                "contents": [{"parts": [{"text": f"User Search Query: {query_text}"}]}],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "response_schema": cleaned_schema,
                    "temperature": 0.0,
                },
            }
            resp = httpx.post(url, json=payload, timeout=8.0)
            if resp.status_code == 404 and "gemini-2.0-flash" in self.model:
                fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                resp = httpx.post(fallback_url, json=payload, timeout=8.0)

            if resp.status_code != 200:
                logger.debug("Gemini Query Parser returned status %s: %s", resp.status_code, resp.text)
                return None

            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return None

            raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
            return ParsedSearchQuery.model_validate_json(raw_text)
        except Exception as e:
            logger.debug(f"LLM query parsing failed: {e}")
            return None

