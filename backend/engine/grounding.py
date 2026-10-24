"""
Quote Grounding and Normalization Engine for TenderBee.

Provides robust Unicode normalization, fuzzy text grounding against document page text,
Indian currency/amount normalization (lakhs, crores, rupees, ₹, INR), numeric grounding
verification, statutory identifier validation (UDYAM, ICAI UDIN), and single-field
grounding pipelines for government and public procurement tenders.
"""
import math
import re
import unicodedata
from typing import Any, Dict, Optional, Set, Union

from rapidfuzz import fuzz

__all__ = [
    "norm",
    "is_grounded",
    "numbers_in",
    "normalize_indian_amount",
    "is_numeric_grounded",
    "validate_udyam_format",
    "validate_udin_format",
    "ground_field",
]


# ==============================================================================
# 1. TEXT NORMALIZATION
# ==============================================================================

def norm(text: str) -> str:
    """
    Enhanced Unicode normalization for tender text and verbatim quote grounding.

    Performs:
    - Unicode NFKC normalization (canonical decomposition + compatibility composition)
    - Case folding (casefold)
    - Removes soft hyphens (\\u00ad)
    - Normalizes all unicode dashes/hyphens (\\u2010-\\u2015, \\u2212) to standard hyphen (-)
    - Normalizes quotation marks (all curly/smart quotes to straight quotes)
    - Collapses all whitespace sequences to a single space
    - Strips leading and trailing whitespace

    Args:
        text: Input string to normalize.

    Returns:
        Cleaned, normalized string. Returns empty string if input is empty or None.
    """
    if not text:
        return ""

    # 1. Unicode NFKC normalization (handles ligatures like ﬁ -> fi)
    s = unicodedata.normalize("NFKC", text)

    # 2. Case folding for case-insensitive matching
    s = s.casefold()

    # 3. Remove soft hyphens (formatting/line-break discretionary hyphens)
    s = s.replace("\u00ad", "")

    # 4. Normalize unicode dashes and hyphens to standard hyphen (-)
    # \u2010 (hyphen), \u2011 (non-breaking), \u2012 (figure dash),
    # \u2013 (en dash), \u2014 (em dash), \u2015 (horizontal bar), \u2212 (minus sign)
    s = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2015\u2212]", "-", s)

    # 5. Normalize quotation marks (curly/smart quotes to straight quotes)
    s = re.sub(r"[\u2018\u2019\u201a\u201b\u2032`]", "'", s)
    s = re.sub(r"[\u201c\u201d\u201e\u201f\u2033«»]", '"', s)

    # 6. Collapse all whitespace to a single space and strip edges
    s = re.sub(r"\s+", " ", s).strip()

    return s


# ==============================================================================
# 2. VERBATIM QUOTE GROUNDING
# ==============================================================================

def is_grounded(quote: str, page_text: str, threshold: float = 92.0) -> bool:
    """
    Verifies that a verbatim quote physically exists on a document page.

    Matching strategy:
    1. Normalize both quote and page text with norm().
    2. Exact normalized substring match first.
    3. Fallback: RapidFuzz partial_ratio >= threshold for minor OCR noise.
    4. Return False if either input is empty.

    Args:
        quote: Verbatim evidence quote to verify.
        page_text: Full text layer of the candidate document page.
        threshold: Minimum fuzzy partial_ratio score (0-100) to accept. Default is 92.0.

    Returns:
        True if the quote is grounded to the page text; False otherwise.
    """
    if not quote or not page_text:
        return False

    q_norm = norm(quote)
    t_norm = norm(page_text)

    if not q_norm or not t_norm:
        return False

    # 1. Exact normalized substring match
    if q_norm in t_norm:
        return True

    # 2. Fuzzy partial ratio fallback for OCR errors
    score = fuzz.partial_ratio(q_norm, t_norm)
    return score >= threshold


# ==============================================================================
# 3. NUMERIC EXTRACTION
# ==============================================================================

def numbers_in(text: str) -> Set[str]:
    """
    Extracts all numeric values from text as cleaned strings without commas or spaces.

    Handles standard integers, Indian comma notation (e.g. 5,20,00,000), standard comma
    notation (e.g. 52,000,000), decimals (e.g. 78,39,23,735.01, 62.4), and standalone digits.

    Args:
        text: Input string containing numbers.

    Returns:
        Set of cleaned numeric strings (e.g. {"52000000"}). Returns empty set if no numbers found.
    """
    if not text or not isinstance(text, str):
        return set()

    # Pattern matches numbers with optional commas/spaces between digits, and optional decimals:
    # Matches digit groups followed by commas and 2 or 3 digits (Indian / standard grouping)
    # or simple decimal numbers, or standalone numbers.
    pattern = re.compile(
        r"(?<![A-Za-z0-9_])(?:\d+(?:,\s*\d{2,3})*(?:\.\d+)?|\.\d+)(?![A-Za-z0-9_])"
    )

    results: Set[str] = set()
    for match in pattern.finditer(text):
        raw_val = match.group()
        # Clean commas and internal spaces
        cleaned = re.sub(r"[,\s]", "", raw_val)
        if cleaned:
            results.add(cleaned)

    return results


# ==============================================================================
# 4. INDIAN CURRENCY NORMALIZATION
# ==============================================================================

def normalize_indian_amount(raw: str) -> Optional[float]:
    """
    Converts Indian currency strings to an INR float value.

    Supported features:
    - Multipliers: lakh/lakhs/lac/lacs (* 100,000), crore/crores/cr/cr. (* 10,000,000),
      thousand/thousands (* 1,000)
    - Strips currency prefixes: Rs., ₹, INR, Re.
    - Strips currency suffixes: /- , rupees, rupee
    - Handles Indian comma notation (e.g. 1,23,45,678.90 -> 12345678.90)
    - Returns None if input is unparseable or non-numeric.

    Args:
        raw: Raw currency string (e.g. "Rs. 5,20,00,000", "62.4 Lakhs", "₹ 50,000").

    Returns:
        Parsed float value in INR, or None if unparseable.
    """
    if not raw or not isinstance(raw, str):
        return None

    s = raw.strip()
    if not s:
        return None

    # Check for known unparseable placeholders
    if s.lower() in ("n/a", "na", "null", "none", "-", "--", "nil"):
        return None

    # Strip currency prefixes: Rs., ₹, INR, Re.
    s = re.sub(r"^(?:rs\.?|inr|₹|re\.?)\s*", "", s, flags=re.IGNORECASE)

    # Strip currency suffixes: /-, rupees, rupee
    s = re.sub(r"\s*(?:/-\s*|\brupees?\b)", "", s, flags=re.IGNORECASE)
    s = s.strip()

    # Determine unit multiplier
    multiplier = 1.0

    # 1. Crores / Cr
    if re.search(r"\b(?:crores?|cr)\b\.?", s, re.IGNORECASE):
        multiplier = 10_000_000.0
        s = re.sub(r"\b(?:crores?|cr)\b\.?", "", s, flags=re.IGNORECASE).strip()
    # 2. Lakhs / Lacs
    elif re.search(r"\b(?:lakhs?|lacs?)\b\.?", s, re.IGNORECASE):
        multiplier = 100_000.0
        s = re.sub(r"\b(?:lakhs?|lacs?)\b\.?", "", s, flags=re.IGNORECASE).strip()
    # 3. Thousands
    elif re.search(r"\bthousands?\b\.?", s, re.IGNORECASE):
        multiplier = 1_000.0
        s = re.sub(r"\bthousands?\b\.?", "", s, flags=re.IGNORECASE).strip()

    # Strip any remaining currency markers
    s = re.sub(r"(?:rs\.?|inr|₹)", "", s, flags=re.IGNORECASE).strip()

    # Clean commas and whitespace from numeric remainder
    cleaned_num = re.sub(r"[,\s]", "", s)
    if not cleaned_num:
        return None

    try:
        val = float(cleaned_num)
        return val * multiplier
    except ValueError:
        return None


# ==============================================================================
# 5. NUMERIC GROUNDING VERIFICATION
# ==============================================================================

def is_numeric_grounded(extracted_value: float, quote: str, tolerance: float = 0.01) -> bool:
    """
    Verifies that an extracted numeric value appears within its verbatim source quote.

    Algorithm:
    1. Extract all numbers from the quote using numbers_in().
    2. For each number, parse as float.
    3. Check if any parsed number matches extracted_value within relative tolerance.
    4. Also try unit-normalized comparisons: if quote contains 'lakh'/'lac',
       'crore'/'cr', or 'thousand', apply the multiplier and compare.
    5. Return True if any match is found, False otherwise.

    Args:
        extracted_value: Numerical value extracted by model or rule.
        quote: Verbatim quote from the source document.
        tolerance: Relative tolerance ratio (default: 0.01 = 1%).

    Returns:
        True if extracted_value is verified in quote within tolerance; False otherwise.
    """
    if extracted_value is None or not quote or not isinstance(quote, str):
        return False

    try:
        target = float(extracted_value)
    except (ValueError, TypeError):
        return False

    q_lower = quote.casefold()

    # Determine potential unit multipliers present in quote
    multipliers = [1.0]
    if re.search(r"\b(?:crores?|cr)\b\.?", q_lower):
        multipliers.append(10_000_000.0)
    if re.search(r"\b(?:lakhs?|lacs?)\b\.?", q_lower):
        multipliers.append(100_000.0)
    if re.search(r"\bthousands?\b\.?", q_lower):
        multipliers.append(1_000.0)

    # 1. Extract candidate numbers from quote
    extracted_nums = numbers_in(quote)

    for num_str in extracted_nums:
        try:
            val = float(num_str)
        except ValueError:
            continue

        # Check raw number and unit-normalized variants
        for mult in multipliers:
            candidate = val * mult
            if math.isclose(candidate, target, rel_tol=tolerance, abs_tol=1e-6):
                return True

    # Also try direct normalization of the entire quote if it represents a single currency string
    parsed_quote_amount = normalize_indian_amount(quote)
    if parsed_quote_amount is not None:
        if math.isclose(parsed_quote_amount, target, rel_tol=tolerance, abs_tol=1e-6):
            return True

    return False


# ==============================================================================
# 6. STATUTORY FORMAT VALIDATORS
# ==============================================================================

def validate_udyam_format(udyam_number: str) -> bool:
    """
    Validates MSME Udyam Registration Number format.

    Format: UDYAM-XX-00-0000000
    - Prefix: UDYAM
    - State Code: 2 uppercase letters (e.g. MH, DL, GJ)
    - District Code: 2 digits
    - Enterprise Serial: 7 digits
    - Case-insensitive input allowed.

    Args:
        udyam_number: String representing the Udyam number.

    Returns:
        True if valid UDYAM format; False otherwise.
    """
    if not udyam_number or not isinstance(udyam_number, str):
        return False

    cleaned = udyam_number.strip()
    return bool(re.match(r"^UDYAM-[A-Z]{2}-\d{2}-\d{7}$", cleaned, re.IGNORECASE))


def validate_udin_format(udin: str) -> bool:
    """
    Validates ICAI Unique Document Identification Number (UDIN) format.

    ICAI UDINs are exactly 18 alphanumeric characters.

    Args:
        udin: String representing the ICAI UDIN.

    Returns:
        True if valid 18-character alphanumeric UDIN; False otherwise.
    """
    if not udin or not isinstance(udin, str):
        return False

    cleaned = udin.strip()
    return bool(re.match(r"^[0-9A-Za-z]{18}$", cleaned))


# ==============================================================================
# 7. FIELD GROUNDING PIPELINE
# ==============================================================================

def ground_field(
    field_value: Any,
    quote: str,
    page_text: str,
    page_num: int,
    threshold: float = 92.0,
) -> Dict[str, Any]:
    """
    Full grounding pipeline for a single extracted field against source document page text.

    Steps:
    1. Check if the verbatim quote is grounded to the page text via is_grounded().
    2. If field_value is numeric (int or float, excluding bool), also verify numeric grounding
       via is_numeric_grounded().
    3. Return a dict containing:
       - 'grounded' (bool): True if all checks pass, False otherwise.
       - 'reason_code' (str or None): None if grounded, 'QUOTE_NOT_GROUNDED', or 'NUMERIC_MISMATCH'.
       - 'confidence_adjustment' (float): 0.0 if fully grounded, -0.5 on grounding failure.

    Args:
        field_value: Parsed or typed value of the field (str, int, float, bool, etc.).
        quote: Verbatim evidence quote extracted for this field.
        page_text: Source text of the document page.
        page_num: 1-indexed page number of the source document.
        threshold: Fuzzy matching threshold for quote grounding (default: 92.0).

    Returns:
        Dictionary with keys 'grounded', 'reason_code', and 'confidence_adjustment'.
    """
    # 1. Quote grounding check against page text
    if not is_grounded(quote, page_text, threshold=threshold):
        return {
            "grounded": False,
            "reason_code": "QUOTE_NOT_GROUNDED",
            "confidence_adjustment": -0.5,
        }

    # 2. Numeric grounding check if field_value is a number (exclude bool since bool is subclass of int)
    if isinstance(field_value, (int, float)) and not isinstance(field_value, bool):
        if not is_numeric_grounded(float(field_value), quote):
            return {
                "grounded": False,
                "reason_code": "NUMERIC_MISMATCH",
                "confidence_adjustment": -0.5,
            }

    # 3. Grounding succeeded
    return {
        "grounded": True,
        "reason_code": None,
        "confidence_adjustment": 0.0,
    }
