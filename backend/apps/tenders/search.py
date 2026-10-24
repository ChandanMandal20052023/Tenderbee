"""
Tender Discovery & Multi-Criteria Search Engine for TenderBee.
Supports natural language query parsing (e.g. 'services in bihar above 1 cr for 2 years')
and structured multi-dimensional filtering across geography, category, capital, tenure, and buyer.
"""
import logging
import os
import re
from pathlib import Path
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

STATE_ALIASES = {
    "up": "Uttar Pradesh",
    "u.p.": "Uttar Pradesh",
    "rj": "Rajasthan",
    "raj": "Rajasthan",
    "rajasthan": "Rajasthan",
    "mh": "Maharashtra",
    "maha": "Maharashtra",
    "wb": "West Bengal",
    "w.b.": "West Bengal",
    "mp": "Madhya Pradesh",
    "m.p.": "Madhya Pradesh",
    "ap": "Andhra Pradesh",
    "a.p.": "Andhra Pradesh",
    "hr": "Haryana",
    "hry": "Haryana",
    "br": "Bihar",
    "bihar": "Bihar",
    "dl": "Delhi",
    "ncr": "Delhi",
    "gj": "Gujarat",
    "tn": "Tamil Nadu",
    "ka": "Karnataka",
    "kl": "Kerala",
    "ts": "Telangana",
    "tg": "Telangana",
    "pb": "Punjab",
    "od": "Odisha",
    "jh": "Jharkhand",
    "uk": "Uttarakhand",
    "ua": "Uttarakhand",
}

CITY_TO_STATE = {
    # Bihar
    "patna": "Bihar", "gaya": "Bihar", "bhagalpur": "Bihar", "muzaffarpur": "Bihar",
    "darbhanga": "Bihar", "purnia": "Bihar", "hajipur": "Bihar", "danapur": "Bihar",
    # Uttar Pradesh
    "lucknow": "Uttar Pradesh", "kanpur": "Uttar Pradesh", "varanasi": "Uttar Pradesh",
    "noida": "Uttar Pradesh", "greater noida": "Uttar Pradesh", "agra": "Uttar Pradesh",
    "prayagraj": "Uttar Pradesh", "allahabad": "Uttar Pradesh", "ghaziabad": "Uttar Pradesh",
    "meerut": "Uttar Pradesh", "bareilly": "Uttar Pradesh", "aligarh": "Uttar Pradesh",
    "gorakhpur": "Uttar Pradesh", "ayodhya": "Uttar Pradesh", "jhansi": "Uttar Pradesh",
    # Rajasthan
    "jaipur": "Rajasthan", "jodhpur": "Rajasthan", "udaipur": "Rajasthan", "kota": "Rajasthan",
    "bikaner": "Rajasthan", "ajmer": "Rajasthan", "bhilwara": "Rajasthan", "alwar": "Rajasthan",
    # Maharashtra
    "mumbai": "Maharashtra", "pune": "Maharashtra", "nagpur": "Maharashtra",
    "thane": "Maharashtra", "nashik": "Maharashtra", "aurangabad": "Maharashtra",
    # Haryana
    "gurugram": "Haryana", "gurgaon": "Haryana", "faridabad": "Haryana",
    "panipat": "Haryana", "ambala": "Haryana", "rohtak": "Haryana", "karnal": "Haryana",
    "hisar": "Haryana", "sonipat": "Haryana",
    # West Bengal
    "kolkata": "West Bengal", "howrah": "West Bengal", "durgapur": "West Bengal",
    "asansol": "West Bengal", "siliguri": "West Bengal",
    # Delhi NCR
    "delhi": "Delhi", "new delhi": "Delhi",
}

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
    Supports hybrid execution:
    1. First attempts LLM-based query comprehension for complex natural language prompts.
    2. Falls back to deterministic regex parser across Indian geography, categories, and financials.
    """

    @classmethod
    def parse(cls, prompt: str, llm_adapter: Optional[Any] = None) -> TenderSearchFilter:
        text = prompt.strip()
        lower = text.lower()

        # Step 1: Attempt LLM-based query parsing if adapter available
        if llm_adapter is not None:
            try:
                llm_parsed = llm_adapter.parse_query(prompt)
                if llm_parsed:
                    logger.info("LLM query parser extracted structured filters: %s", llm_parsed.model_dump())
                    return TenderSearchFilter(
                        query=llm_parsed.query,
                        state=llm_parsed.state,
                        city_or_district=llm_parsed.city_or_district,
                        category=llm_parsed.category,
                        min_value_inr=llm_parsed.min_value_inr,
                        max_value_inr=llm_parsed.max_value_inr,
                        min_tenure_months=llm_parsed.min_tenure_months,
                        buyer_name=llm_parsed.buyer_name,
                    )
            except Exception as e:
                logger.debug("LLM query parsing encountered exception, falling back to deterministic parser: %s", e)

        # Step 2: Deterministic Rule-Based Parsing
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
        for alias, state_name in STATE_ALIASES.items():
            if re.search(r"\b" + re.escape(alias) + r"\b", text):
                return state_name
        return None

    @classmethod
    def _extract_category(cls, text: str) -> Optional[str]:
        if re.search(r"\b(service|services|housekeeping|sanitation|security|manpower|facility|it)\b", text):
            return "Services"
        if re.search(r"\b(work|works|civil|construction|road|bridge|building|pipeline|drainage|expressway|flyover)\b", text):
            return "Works"
        if re.search(r"\b(good|goods|supply|supplies|equipment|hardware|vehicle|material|solar)\b", text):
            return "Goods"
        return None

    @classmethod
    def _extract_city(cls, text: str, state: Optional[str]) -> Optional[str]:
        for c in CITY_TO_STATE:
            if re.search(r"\b" + re.escape(c) + r"\b", text):
                return "Gurugram" if c == "gurgaon" else c.title()
        return None

    @classmethod
    def _infer_state_from_city(cls, city: str) -> Optional[str]:
        return CITY_TO_STATE.get(city.lower())

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
            "having", "contract", "like", "any", "all", "around", "near", "location", "is", "these",
            "those", "there", "wanted", "want", "look", "looking", "procurement", "notice"
        ]
        if state:
            remove_terms.extend([state.lower(), f"in {state.lower()}"])
            for alias, full_state in STATE_ALIASES.items():
                if full_state.lower() == state.lower():
                    remove_terms.extend([alias, f"in {alias}"])
        if category:
            remove_terms.extend([category.lower(), f"{category.lower()}s"])
        if city:
            remove_terms.extend([city.lower(), f"in {city.lower()}"])

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

    def __init__(
        self,
        storage: Optional[TenderStorage] = None,
        llm_adapter: Optional[Any] = None,
        live_search_engine: Optional[Any] = None,
    ):
        self.storage = storage or TenderStorage()
        if llm_adapter is not None:
            self.llm_adapter = llm_adapter
        else:
            try:
                from backend.services.llm import LLMAdapter
                self.llm_adapter = LLMAdapter()
            except Exception:
                self.llm_adapter = None

        if live_search_engine is not None:
            self.live_search_engine = live_search_engine
        else:
            try:
                from backend.services.live_search import LiveTenderSearchEngine
                self.live_search_engine = LiveTenderSearchEngine(storage=self.storage)
            except Exception:
                self.live_search_engine = None

    def search(self, filters: TenderSearchFilter, raw_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute search query across local index and connected portals.
        """
        # 1. Search local indexed database
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

        # 2. If no local matches, automatically trigger live procurement portal search!
        if total_count == 0 and self.live_search_engine:
            logger.info("No local match found. Dispatching live portal search for filters %s", filters.model_dump())
            live_tenders = self.live_search_engine.search_live(
                query=filters.query,
                state=filters.state,
                category=filters.category,
                city=filters.city_or_district,
                raw_prompt=raw_prompt,
                limit=filters.limit,
            )
            if live_tenders:
                return {
                    "success": True,
                    "applied_filters": filters.model_dump(),
                    "total_matches": len(live_tenders),
                    "page": filters.page,
                    "limit": filters.limit,
                    "source": "live_portal_discovery",
                    "results": live_tenders,
                }

        return {
            "success": True,
            "applied_filters": filters.model_dump(),
            "total_matches": total_count,
            "page": filters.page,
            "limit": filters.limit,
            "source": "local_index",
            "results": local_results,
        }

    def search_by_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        End-to-end natural language search:
        1. Parses prompt to structured filters using LLM with deterministic fallback.
        2. Executes multi-criteria search with live portal discovery.
        3. Returns ranked tenders.
        """
        parsed_filters = QueryParser.parse(prompt, llm_adapter=self.llm_adapter)
        logger.info("Parsed prompt '%s' to filters: %s", prompt, parsed_filters.model_dump())
        res = self.search(parsed_filters, raw_prompt=prompt)
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

        # If detailed mode requested and no PDF has been parsed yet, robustly acquire & parse it
        if mode == "detailed":
            if identifier.endswith(".pdf") or (os.path.exists(identifier) and not os.path.isdir(identifier)):
                service = TenderService(storage=self.storage)
                intake_res = service.intake_tender_pdf(identifier)
                if intake_res.get("success"):
                    tender = self.storage.get_tender(intake_res["tender_id"], mode="detailed")
                    if tender:
                        tender["rule_pack"] = intake_res.get("rule_pack")
            else:
                if not tender:
                    service = TenderService(storage=self.storage)
                    intake_res = service.intake_tender(identifier)
                    if intake_res.get("success"):
                        tender = self.storage.get_tender(intake_res["tender_id"], mode="detailed")
                        if tender:
                            tender["rule_pack"] = intake_res.get("rule_pack")

                # If tender exists but has no parsed snapshot or clauses, robustly acquire and parse PDF
                if tender and (tender.get("pdf_status") != "PARSED" or not tender.get("extraction")):
                    from backend.services.pdf_resolver import TenderPDFResolver
                    resolver = TenderPDFResolver(storage=self.storage)
                    resolved_pdf = resolver.resolve_and_acquire_pdf(tender)
                    if resolved_pdf:
                        service = TenderService(storage=self.storage)
                        intake_res = service.intake_tender_pdf(
                            resolved_pdf,
                            tender_id=tender.get("tender_id"),
                        )
                        if intake_res.get("success"):
                            tender = self.storage.get_tender(tender["tender_id"], mode="detailed")
                            if tender:
                                tender["rule_pack"] = intake_res.get("rule_pack")

            if tender and tender.get("has_pdf_document") and "rule_pack" not in tender:
                service = TenderService(storage=self.storage)
                rule_pack = service.get_rule_pack_by_tender_id(tender["tender_id"])
                if rule_pack:
                    tender["rule_pack"] = rule_pack.model_dump()

            if tender:
                from backend.engine.schema import TenderPDFExtractionResult
                tender["json_schema"] = TenderPDFExtractionResult.get_json_schema()

        return tender

