"""
Tender Discovery & Multi-Criteria Search Engine for TenderBee.
Supports natural language query parsing (e.g. 'services in bihar above 1 cr for 2 years')
and structured multi-dimensional filtering across geography, category, capital, tenure, and buyer.
"""
import logging
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.services.storage import TenderStorage

logger = logging.getLogger(__name__)

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Jammu and Kashmir", "Ladakh"
]

CATEGORIES = ["Services", "Works", "Goods"]


class TenderSearchFilter(BaseModel):
    query: Optional[str] = Field(default=None, description="Free text keywords")
    state: Optional[str] = Field(default=None, description="Indian state name (e.g. Bihar)")
    city_or_district: Optional[str] = Field(default=None, description="City or district (e.g. Patna)")
    category: Optional[str] = Field(default=None, description="Services, Works, or Goods")
    min_value_inr: Optional[float] = Field(default=None, description="Minimum estimated contract value")
    max_value_inr: Optional[float] = Field(default=None, description="Maximum estimated contract value")
    min_tenure_months: Optional[int] = Field(default=None, description="Minimum contract period in months")
    max_tenure_months: Optional[int] = Field(default=None, description="Maximum contract period in months")
    buyer_name: Optional[str] = Field(default=None, description="Issuing authority / department")
    active_only: bool = Field(default=True, description="Filter only active tenders with upcoming deadlines")
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class TenderSearchResult(BaseModel):
    tender_id: str
    tender_number: str
    title: str
    buyer_name: str
    state: str
    category: str
    estimated_value_inr: Optional[float] = None
    emd_amount_inr: Optional[float] = None
    tenure_months: Optional[int] = None
    submission_deadline: Optional[str] = None
    portal: str
    source_url: Optional[str] = None
    status: str = "ACTIVE"


class QueryParser:
    """
    Parses natural language procurement requests into structured TenderSearchFilter.
    Examples:
      - 'tenders related to services in bihar' -> category='Services', state='Bihar'
      - 'civil works in patna above 50 lakhs for 2 years' -> category='Works', state='Bihar', min_value=5000000, tenure=24
    """

    @classmethod
    def parse(cls, prompt: str) -> TenderSearchFilter:
        text = prompt.strip()
        lower = text.lower()

        state = cls._extract_state(lower)
        category = cls._extract_category(lower)
        city = cls._extract_city(lower, state)
        if not state and city:
            state = cls._infer_state_from_city(city)
        min_val, max_val = cls._extract_values(lower)
        min_tenure = cls._extract_tenure(lower)
        keywords = cls._extract_keywords(text, state, category, city)

        return TenderSearchFilter(
            query=keywords if keywords else None,
            state=state,
            city_or_district=city,
            category=category,
            min_value_inr=min_val,
            max_value_inr=max_val,
            min_tenure_months=min_tenure,
        )

    @classmethod
    def _extract_state(cls, text: str) -> Optional[str]:
        for s in INDIAN_STATES:
            if re.search(r"\b" + re.escape(s.lower()) + r"\b", text):
                return s
        # Common aliases
        if re.search(r"\bup\b", text):
            return "Uttar Pradesh"
        if re.search(r"\bmh\b", text):
            return "Maharashtra"
        if re.search(r"\bwb\b", text):
            return "West Bengal"
        return None

    @classmethod
    def _extract_category(cls, text: str) -> Optional[str]:
        if re.search(r"\b(service|services|housekeeping|sanitation|security|manpower|facility|it)\b", text):
            return "Services"
        if re.search(r"\b(work|works|civil|construction|road|bridge|building|pipeline|drainage)\b", text):
            return "Works"
        if re.search(r"\b(good|goods|supply|supplies|equipment|hardware|vehicle|material)\b", text):
            return "Goods"
        return None

    @classmethod
    def _extract_city(cls, text: str, state: Optional[str]) -> Optional[str]:
        # Major cities
        bihar_cities = ["patna", "gaya", "bhagalpur", "muzaffarpur", "darbhanga", "purnia", "hajipur", "danapur"]
        for c in bihar_cities:
            if re.search(r"\b" + re.escape(c) + r"\b", text):
                return c.capitalize()
        return None

    @classmethod
    def _infer_state_from_city(cls, city: str) -> Optional[str]:
        city_lower = city.lower()
        bihar_cities = {"patna", "gaya", "bhagalpur", "muzaffarpur", "darbhanga", "purnia", "hajipur", "danapur"}
        mh_cities = {"mumbai", "pune", "nagpur", "thane", "nashik"}
        up_cities = {"lucknow", "kanpur", "varanasi", "noida", "agra"}
        if city_lower in bihar_cities:
            return "Bihar"
        if city_lower in mh_cities:
            return "Maharashtra"
        if city_lower in up_cities:
            return "Uttar Pradesh"
        return None

    @classmethod
    def _extract_values(cls, text: str) -> tuple[Optional[float], Optional[float]]:
        min_val = None
        max_val = None

        # Regex for Crore (Cr / Crore / Crores)
        cr_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:cr|crore|crores)\b", text)
        # Regex for Lakh (Lakh / Lakhs / L / Lac / Lacs)
        lakh_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:lakh|lakhs|lac|lacs|l)\b", text)

        # Look for above / minimum / >
        above_m = re.search(r"(?:above|min|minimum|greater than|>|more than)\s*₹?\s*(\d+(?:\.\d+)?)\s*(cr|crore|crores|lakh|lakhs|l)?", text)
        if above_m:
            num = float(above_m.group(1))
            unit = (above_m.group(2) or "").lower()
            if "cr" in unit:
                min_val = num * 10000000.0
            elif "l" in unit or "lac" in unit:
                min_val = num * 100000.0
            else:
                min_val = num

        # Look for below / maximum / <
        below_m = re.search(r"(?:below|max|maximum|less than|<|upto)\s*₹?\s*(\d+(?:\.\d+)?)\s*(cr|crore|crores|lakh|lakhs|l)?", text)
        if below_m:
            num = float(below_m.group(1))
            unit = (below_m.group(2) or "").lower()
            if "cr" in unit:
                max_val = num * 10000000.0
            elif "l" in unit or "lac" in unit:
                max_val = num * 100000.0
            else:
                max_val = num

        # If bare number with Cr was found and no above/below
        if min_val is None and cr_matches:
            min_val = float(cr_matches[0]) * 10000000.0
        elif min_val is None and lakh_matches:
            min_val = float(lakh_matches[0]) * 100000.0

        return min_val, max_val

    @classmethod
    def _extract_tenure(cls, text: str) -> Optional[int]:
        # Years
        yr_m = re.search(r"(\d+)\s*(?:year|years|yr|yrs)\b", text)
        if yr_m:
            return int(yr_m.group(1)) * 12
        # Months
        m_m = re.search(r"(\d+)\s*(?:month|months|mo|mos)\b", text)
        if m_m:
            return int(m_m.group(1))
        return None

    @classmethod
    def _extract_keywords(cls, original: str, state: Optional[str], category: Optional[str], city: Optional[str]) -> str:
        s = original
        remove_terms = [
            "tenders", "tender", "related", "to", "released", "in", "for", "give", "me", "show",
            "active", "above", "below", "greater", "less", "than", "with", "tenure", "duration",
            "period", "capital", "value", "budget", "find", "search", "between", "from", "upto",
            "having", "contract", "like", "any", "all", "around", "near"
        ]
        if state:
            remove_terms.extend([state.lower(), f"in {state.lower()}"])
        if category:
            remove_terms.extend([category.lower(), f"{category.lower()}s"])
        if city:
            remove_terms.extend([city.lower()])

        pattern = r"\b(" + "|".join(re.escape(w) for w in remove_terms) + r")\b"
        cleaned = re.sub(pattern, " ", s, flags=re.IGNORECASE)
        # Remove numbers and currency words
        cleaned = re.sub(r"\b\d+(?:\.\d+)?\s*(cr|crore|crores|lakh|lakhs|l|lac|lacs|year|years|yr|yrs|month|months|mo|mos|rs|inr|₹)?\b", " ", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"[^\w\s]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned


class TenderSearchService:
    """
    Orchestrates multi-criteria tender discovery across the local database index,
    live GeM portal search, and state e-procurement systems (like eproc2.bihar.gov.in).
    """

    def __init__(self, storage: Optional[TenderStorage] = None):
        self.storage = storage or TenderStorage()

    def search(self, filters: TenderSearchFilter) -> Dict[str, Any]:
        """
        Execute search query across local index and connected portals.
        """
        # Search local indexed database
        local_results = self.storage.search_indexed_tenders(
            query=filters.query,
            state=filters.state,
            category=filters.category,
            min_value_inr=filters.min_value_inr,
            max_value_inr=filters.max_value_inr,
            min_tenure_months=filters.min_tenure_months,
            buyer_name=filters.buyer_name,
            limit=filters.limit,
            offset=(filters.page - 1) * filters.limit,
        )

        total_count = len(local_results)

        return {
            "success": True,
            "applied_filters": filters.model_dump(),
            "total_matches": total_count,
            "page": filters.page,
            "limit": filters.limit,
            "results": local_results,
        }

    def search_by_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        End-to-end natural language search:
        1. Parses prompt to structured filters.
        2. Executes multi-criteria search.
        3. Returns ranked tenders.
        """
        parsed_filters = QueryParser.parse(prompt)
        logger.info("Parsed prompt '%s' to filters: %s", prompt, parsed_filters.model_dump())
        res = self.search(parsed_filters)
        res["interpreted_prompt"] = prompt
        return res

    def get_tender(self, identifier: str, mode: str = "skim") -> Optional[Dict[str, Any]]:
        """
        Retrieves tender by tender_id or external tender_number.
        Supports two viewing modes:
        - 'skim': Fast high-level overview (financials, buyer, deadline, tenure, status)
        - 'detailed': Complete breakdown including parsed PDF clauses, page citations, and rule pack.
        """
        from backend.apps.tenders.services import TenderService

        tender = self.storage.get_tender(identifier, mode=mode)

        # If detailed mode requested and no PDF has been parsed yet, try to acquire & parse it
        if mode == "detailed":
            if not tender or tender.get("pdf_status") == "PENDING_INTAKE" or identifier.endswith(".pdf"):
                service = TenderService(storage=self.storage)
                if identifier.endswith(".pdf"):
                    intake_res = service.intake_tender_pdf(identifier)
                else:
                    intake_res = service.intake_tender(identifier)

                if intake_res.get("success"):
                    tender = self.storage.get_tender(intake_res["tender_id"], mode="detailed")
                    if tender:
                        tender["rule_pack"] = intake_res.get("rule_pack")
            elif tender and tender.get("has_pdf_document"):
                service = TenderService(storage=self.storage)
                rule_pack = service.get_rule_pack_by_tender_id(tender["tender_id"])
                if rule_pack:
                    tender["rule_pack"] = rule_pack.model_dump()

            if tender:
                from backend.engine.schema import TenderPDFExtractionResult
                tender["json_schema"] = TenderPDFExtractionResult.get_json_schema()

        return tender

