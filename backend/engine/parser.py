"""
Rule condition, expression, and PDF document parser for TenderBee.
Extracts page-level text, metadata, procurement parameters, and compliance clauses
with exact verbatim quotes and source page citations, returning a validated JSON schema.
"""
import io
import re
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from pypdf import PdfReader
from rapidfuzz import fuzz

from backend.engine.schema import (
    TenderClauseQuote,
    TenderEligibilityRules,
    TenderPDFExtractionResult,
    TenderPDFPage,
)

logger = logging.getLogger(__name__)


# ==============================================================================
# NORMALIZATION & GROUNDING HELPERS
# ==============================================================================

def norm(text: str) -> str:
    """
    Unicode NFKC normalization, lowercase, dash unification, and whitespace collapsing.
    Guarantees quote matching works identically across PDF encodings.
    """
    import unicodedata
    if not text:
        return ""
    # Unicode NFKC
    s = unicodedata.normalize("NFKC", text)
    # Casefold
    s = s.casefold()
    # Normalize unicode hyphens/dashes to standard hyphen
    s = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015\u2212\u00ad]", "-", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def is_grounded(quote: str, page_text: str, threshold: float = 92.0) -> bool:
    """
    Verifies that a verbatim quote physically exists on the given page text.
    1. Exact normalized substring match.
    2. Fallback: RapidFuzz partial_ratio >= threshold for minor OCR noise.
    """
    if not quote or not page_text:
        return False
    q_norm = norm(quote)
    t_norm = norm(page_text)
    if not q_norm or not t_norm:
        return False

    # 1. Exact substring
    if q_norm in t_norm:
        return True

    # 2. Fuzzy partial ratio fallback
    score = fuzz.partial_ratio(q_norm, t_norm)
    return score >= threshold


# ==============================================================================
# TENDER PDF EXTRACTOR
# ==============================================================================

class TenderPDFExtractor:
    """
    Extracts structured tender specifications, procurement rules, and verbatim
    evidence quotes from Indian government and railway tender notice PDFs.
    """

    def __init__(self, min_char_threshold_per_page: int = 40):
        self.min_char_threshold = min_char_threshold_per_page

    def extract_from_pdf(self, pdf_input: Union[str, Path, bytes, io.BytesIO]) -> TenderPDFExtractionResult:
        """
        Parses a tender PDF file or bytes, extracts page-by-page text, and applies
        clause recognition to assemble a typed TenderPDFExtractionResult.
        """
        reader = self._load_reader(pdf_input)
        total_pages = len(reader.pages)
        if total_pages == 0:
            raise ValueError("PDF contains no pages.")

        pages_data: List[TenderPDFPage] = []
        full_text_by_page: List[Tuple[int, str]] = []
        digital_pages = 0

        # Step 1: Extract text layer page by page
        for idx, page in enumerate(reader.pages):
            page_num = idx + 1
            raw_text = page.extract_text() or ""
            cleaned_text = re.sub(r"[ \t]+", " ", raw_text).strip()
            char_count = len(cleaned_text)

            is_scanned = char_count < self.min_char_threshold
            if not is_scanned:
                digital_pages += 1

            full_text_by_page.append((page_num, cleaned_text))
            pages_data.append(
                TenderPDFPage(
                    page_number=page_num,
                    text_snippet=cleaned_text[:200].replace("\n", " "),
                    char_count=char_count,
                    is_scanned=is_scanned,
                )
            )

        digital_coverage = round(digital_pages / total_pages, 3)

        # Step 2: Extract Tender Metadata & Procurement Parameters
        metadata = self._extract_tender_metadata(full_text_by_page)

        # Step 3: Extract Clauses & Eligibility Requirements with Page Citations
        clauses, eligibility, mandatory_docs = self._extract_clauses(full_text_by_page, metadata.get("estimated_value_inr"))

        return TenderPDFExtractionResult(
            tender_number=metadata.get("tender_number"),
            tender_title=metadata.get("tender_title", "Procurement Tender Notice"),
            buyer_name=metadata.get("buyer_name"),
            submission_deadline=metadata.get("submission_deadline"),
            opening_date=metadata.get("opening_date"),
            contract_period=metadata.get("contract_period"),
            estimated_value_inr=metadata.get("estimated_value_inr"),
            emd_amount_inr=metadata.get("emd_amount_inr"),
            mse_exemption_allowed=metadata.get("mse_exemption_allowed", False) or ("udyam_certificate" in mandatory_docs),
            portal_website=metadata.get("portal_website"),
            mandatory_documents=mandatory_docs,
            eligibility_rules=eligibility,
            verbatim_clauses=clauses,
            total_pages=total_pages,
            digital_text_coverage=digital_coverage,
            pages=pages_data,
        )

    def get_json_schema(self) -> Dict[str, Any]:
        """Returns the canonical Pydantic JSON schema."""
        return TenderPDFExtractionResult.model_json_schema()

    def _load_reader(self, pdf_input: Union[str, Path, bytes, io.BytesIO]) -> PdfReader:
        if isinstance(pdf_input, (str, Path)):
            path = Path(pdf_input)
            if not path.is_file():
                raise FileNotFoundError(f"PDF file not found: {path}")
            return PdfReader(str(path))
        elif isinstance(pdf_input, bytes):
            return PdfReader(io.BytesIO(pdf_input))
        elif isinstance(pdf_input, io.BytesIO):
            return PdfReader(pdf_input)
        else:
            raise TypeError(f"Unsupported PDF input type: {type(pdf_input)}")

    def _parse_inr_amount(self, text: str) -> Optional[float]:
        """Normalizes Indian currency string (e.g. '52,26,15,823.34' or 'Rs. 27,63,100') to float."""
        if not text:
            return None
        cleaned = re.sub(r"[^\d.]", "", text.strip())
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    def _extract_tender_metadata(self, pages: List[Tuple[int, str]]) -> Dict[str, Any]:
        """Extracts top-level tender attributes from the top sheet and early pages."""
        meta: Dict[str, Any] = {}
        early_pages = pages[:5]
        combined_early_text = "\n".join(p[1] for p in early_pages)

        # 1. Tender Number
        tender_no_patterns = [
            r"e-Tender Notice No[:.]?\s*([A-Za-z0-9_\-\/\.]+)",
            r"e-Tender No[:.]?\s*([A-Za-z0-9_\-\/\.]+)",
            r"Tender Notice No[:.]?\s*([A-Za-z0-9_\-\/\.]+)",
            r"Tender No[:.]?\s*([A-Za-z0-9_\-\/\.]+)",
            r"Bid No[:.]?\s*([A-Za-z0-9_\-\/\.]+)",
            r"(GEM/\d{4}/[BR]/\d+)",
            r"(\d{4}_[A-Za-z0-9]+_\d+_\d+)",
        ]
        for pat in tender_no_patterns:
            m = re.search(pat, combined_early_text, re.IGNORECASE)
            if m:
                meta["tender_number"] = m.group(1).strip()
                break

        # 2. Name of Work / Tender Title
        title_patterns = [
            r"Name of Work:\s*(.*?)(?=(?:Type of|Cost of|Estimated|Bid Security|Completion|Validity|e-tender website|\n\s*\n))",
            r"Tender Title[:\s]+(.*?)(?=\n|\r|$)",
            r"Title of Work[:\s]+(.*?)(?=\n|\r|$)",
        ]
        for pat in title_patterns:
            m = re.search(pat, combined_early_text, re.DOTALL | re.IGNORECASE)
            if m:
                title = m.group(1).replace("\n", " ").strip()
                title = re.sub(r"\s+", " ", title)
                if len(title) > 10:
                    meta["tender_title"] = title
                    break

        # 3. Buyer / Department
        buyer_patterns = [
            r"(WESTERN RAILWAY\s*MUMBAI CENTRAL DIVISION(?:\s*\([^)]*\))?)",
            r"Tender Inviting Authority[\s\S]*?((?:Divisional|General|Chief|Executive|Superintending)[\s\S]*?)(?=For and on behalf|Date|\n\s*\n)",
            r"Buyer Name[:\s]+([^\n]+)",
            r"Department[:\s]+([^\n]+)",
        ]
        for pat in buyer_patterns:
            m = re.search(pat, combined_early_text, re.IGNORECASE)
            if m:
                bname = re.sub(r"\s+", " ", m.group(1).replace("\n", " ")).strip()
                meta["buyer_name"] = bname
                break

        # 4. Estimated Cost / Value
        cost_m = re.search(r"Estimated Cost of Work[:\s]*Rs\.?\s*([0-9,]+(?:\.[0-9]+)?)", combined_early_text, re.IGNORECASE)
        if cost_m:
            meta["estimated_value_inr"] = self._parse_inr_amount(cost_m.group(1))

        # 5. Earnest Money Deposit (EMD)
        emd_m = re.search(r"(?:Bid Security Amount\s*/\s*)?Earnest Money(?: Deposit)?[:\s]*Rs\.?\s*([0-9,]+(?:\.[0-9]+)?)", combined_early_text, re.IGNORECASE)
        if emd_m:
            meta["emd_amount_inr"] = self._parse_inr_amount(emd_m.group(1))

        # 6. Contract Period
        period_m = re.search(r"(?:Completion Period\s*/\s*)?Contract Period[:\s]*([^\n]+)", combined_early_text, re.IGNORECASE)
        if period_m:
            meta["contract_period"] = period_m.group(1).strip()

        # 7. Portal Website
        portal_m = re.search(r"https?://\s*([a-zA-Z0-9\.\-]+(?:gov\.in|nic\.in|infralens\.in))", combined_early_text, re.IGNORECASE)
        if portal_m:
            meta["portal_website"] = f"https://{portal_m.group(1).strip()}"

        return meta

    def _extract_clauses(
        self, pages: List[Tuple[int, str]], estimated_value: Optional[float]
    ) -> Tuple[List[TenderClauseQuote], TenderEligibilityRules, List[str]]:
        """Scans all pages for statutory, financial, and technical eligibility clauses."""
        clauses: List[TenderClauseQuote] = []
        mandatory_docs: List[str] = []
        eligibility = TenderEligibilityRules()

        clause_specs = [
            (
                r"(Aggregate financial turnover not less than.*?Rs\.?\s*([0-9,]+(?:\.[0-9]+)?))",
                "turnover_requirement",
                "turnover",
            ),
            (
                r"(T2:\s*Minimum 5% of the estimated bid value.*?Rs\.?\s*([0-9,]+(?:\.[0-9]+)?))",
                "liquidity_requirement",
                "liquidity",
            ),
            (
                r"(Completed work:\s*One similar single service contract.*?Rs\.?\s*([0-9,]+(?:\.[0-9]+)?))",
                "work_experience_requirement",
                "work_exp",
            ),
            (
                r"(Audited Balance Sheet.*?reflecting financial turnover certified by Chartered Accountant.*?(?:membership number|UDIN))",
                "ca_balance_sheet_requirement",
                "ca_sheet",
            ),
            (
                r"(Only Railway PSUs are eligible to participate in this tender.*?\.)",
                "entity_eligibility_restriction",
                "psu_restriction",
            ),
            (
                r"(MSEs registered with.*?exempted from payment of(?: minimum)? EMD.*?\.)",
                "mse_emd_exemption_clause",
                "mse_emd",
            ),
            (
                r"(1\.8\s*MSEs registered with the agencies will be exempted from payment of Tender Fee & Earnest Money.*?\.)",
                "mse_fee_exemption_clause",
                "mse_fee",
            ),
            (
                r"(Undertaking for Truthfulness/\s*Correctness of the Documents\s*–\s*Annexure-I)",
                "annexure_i_truthfulness",
                "annexure_i",
            ),
            (
                r"(Format for Banking Reference for Liquidity\s*-\s*Annexure-X)",
                "annexure_x_liquidity",
                "annexure_x",
            ),
            (
                r"(Bid Form\s*-\s*Annexure-II)",
                "annexure_ii_bid_form",
                "annexure_ii",
            ),
        ]

        for page_num, raw_text in pages:
            if not raw_text:
                continue
            normalized_text = re.sub(r"\s+", " ", raw_text)

            for pattern, clause_type, category in clause_specs:
                m = re.search(pattern, normalized_text, re.IGNORECASE)
                if not m:
                    continue

                quote_text = m.group(1).strip()
                clauses.append(
                    TenderClauseQuote(
                        clause_type=clause_type,
                        page=page_num,
                        quote=quote_text,
                    )
                )

                if category == "turnover":
                    amt = self._parse_inr_amount(m.group(2))
                    if amt and amt > 10000:
                        if eligibility.min_annual_turnover_inr is None or amt > eligibility.min_annual_turnover_inr:
                            eligibility.min_annual_turnover_inr = amt
                    if "ca_turnover_certificate" not in mandatory_docs:
                        mandatory_docs.append("ca_turnover_certificate")

                elif category == "liquidity":
                    amt = self._parse_inr_amount(m.group(2))
                    if amt and amt > 10000:
                        eligibility.min_liquidity_inr = amt
                    if "banking_reference_annexure_x" not in mandatory_docs:
                        mandatory_docs.append("banking_reference_annexure_x")

                elif category == "work_exp":
                    amt = self._parse_inr_amount(m.group(2))
                    if amt and amt > 10000:
                        eligibility.min_work_experience_inr = amt

                elif category == "ca_sheet":
                    eligibility.udin_mandatory = True
                    if "ca_turnover_certificate" not in mandatory_docs:
                        mandatory_docs.append("ca_turnover_certificate")

                elif category in ("mse_emd", "mse_fee"):
                    if "udyam_certificate" not in mandatory_docs:
                        mandatory_docs.append("udyam_certificate")

                elif category == "psu_restriction":
                    if "Railway PSUs" not in eligibility.eligible_entity_types:
                        eligibility.eligible_entity_types.append("Railway PSUs")

                elif category == "annexure_i":
                    if "truthfulness_undertaking_annexure_i" not in mandatory_docs:
                        mandatory_docs.append("truthfulness_undertaking_annexure_i")

                elif category == "annexure_ii":
                    if "bid_form_annexure_ii" not in mandatory_docs:
                        mandatory_docs.append("bid_form_annexure_ii")

                elif category == "annexure_x":
                    if "banking_reference_annexure_x" not in mandatory_docs:
                        mandatory_docs.append("banking_reference_annexure_x")

        if eligibility.min_annual_turnover_inr is None and estimated_value:
            eligibility.min_annual_turnover_inr = round(estimated_value * 1.5, 2)

        return clauses, eligibility, mandatory_docs
