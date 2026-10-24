"""
Unit tests for backend.engine.grounding: Quote Grounding and Normalization Engine.

Tests Unicode normalization, verbatim quote grounding against page text,
numbers extraction, Indian currency normalization (lakhs, crores, INR),
numeric grounding verification, UDYAM and ICAI UDIN format validation,
and single-field grounding pipelines.
"""
import pytest

from backend.engine.grounding import (
    ground_field,
    is_grounded,
    is_numeric_grounded,
    norm,
    normalize_indian_amount,
    numbers_in,
    validate_udin_format,
    validate_udyam_format,
)


# ==============================================================================
# 1. norm() TESTS
# ==============================================================================

def test_norm_unicode_dashes():
    """Verifies that unicode dashes (em-dash, en-dash, minus, etc.) become standard ASCII hyphens."""
    raw = "Clause 4.1 \u2013 Financial Criteria \u2014 Annexure A \u2212 Schedule"
    assert norm(raw) == "clause 4.1 - financial criteria - annexure a - schedule"


def test_norm_casefold():
    """Verifies that mixed case text is properly converted to lowercase via casefold."""
    raw = "WESTERN RAILWAY - HeadQuarters Office MUMBAI"
    assert norm(raw) == "western railway - headquarters office mumbai"


def test_norm_whitespace_collapse():
    """Verifies that multiple spaces, tabs, and newlines collapse into a single space."""
    raw = "  Minimum \t\t turnover   requirement:   Rs. 50,00,000 \n  "
    assert norm(raw) == "minimum turnover requirement: rs. 50,00,000"


def test_norm_curly_quotes():
    """Verifies that curly quotation marks (single and double) normalize to straight quotes."""
    raw = "“Tender Requirements” and ‘Technical Eligibility’"
    assert norm(raw) == '"tender requirements" and \'technical eligibility\''


def test_norm_empty_string():
    """Verifies that empty string or whitespace-only inputs normalize to empty string."""
    assert norm("") == ""
    assert norm("   ") == ""
    assert norm(None) == ""


def test_norm_nfkc():
    """Verifies that Unicode NFKC ligatures such as 'ﬁ' and 'ﬂ' normalize to 'fi' and 'fl'."""
    raw = "ﬁnancial certiﬁcate speciﬁcation ﬂow"
    assert norm(raw) == "financial certificate specification flow"


def test_norm_soft_hyphens():
    """Verifies that soft hyphens (\u00ad) inserted for line-breaking are stripped cleanly."""
    raw = "con\u00adtractor and sub\u00adcon\u00adtractor"
    assert norm(raw) == "contractor and subcontractor"


# ==============================================================================
# 2. is_grounded() TESTS
# ==============================================================================

def test_grounded_exact_match():
    """Verifies that an exact substring in the page text passes quote grounding."""
    page_text = (
        "WESTERN RAILWAY\n"
        "The contractor shall submit a certificate from Chartered Accountant with UDIN."
    )
    quote = "submit a certificate from Chartered Accountant with UDIN"
    assert is_grounded(quote, page_text) is True


def test_grounded_case_insensitive():
    """Verifies that quote grounding succeeds regardless of case differences."""
    page_text = "The Contractor Shall Submit A CA Certificate With UDIN."
    quote = "the contractor shall submit a ca certificate with udin"
    assert is_grounded(quote, page_text) is True


def test_grounded_whitespace_diff():
    """Verifies that quote grounding succeeds even with different spacing or line breaks."""
    page_text = "Turnover Requirement:\n  150%   of   Advertised Value"
    quote = "Turnover Requirement: 150% of Advertised Value"
    assert is_grounded(quote, page_text) is True


def test_grounded_fuzzy_ocr_error():
    """Verifies that a one-character OCR noise error in a quote passes fuzzy matching (>=92%)."""
    page_text = "The contractor shall submit an audited balance sheet."
    # OCR typo: 'audlted' instead of 'audited'
    quote = "The contractor shall submit an audlted balance sheet."
    assert is_grounded(quote, page_text, threshold=92.0) is True


def test_grounded_wrong_page():
    """Verifies that a quote completely absent from the page text fails grounding."""
    page_text = "Technical eligibility: Similar nature of work completed in last 7 years."
    quote = "Financial turnover must exceed Rs. 100 Crore in FY 2024-25"
    assert is_grounded(quote, page_text) is False


def test_grounded_empty_quote():
    """Verifies that an empty or whitespace-only quote returns False."""
    page_text = "Valid page text containing contractor guidelines."
    assert is_grounded("", page_text) is False
    assert is_grounded("   ", page_text) is False
    assert is_grounded(None, page_text) is False


def test_grounded_empty_page():
    """Verifies that an empty or whitespace-only page text returns False."""
    quote = "Valid quote"
    assert is_grounded(quote, "") is False
    assert is_grounded(quote, "   ") is False
    assert is_grounded(quote, None) is False


# ==============================================================================
# 3. numbers_in() TESTS
# ==============================================================================

def test_numbers_in_indian_format():
    """Verifies that Indian currency comma formatting (e.g. 'Rs. 5,20,00,000') extracts '52000000'."""
    raw = "Average annual turnover: Rs. 5,20,00,000"
    extracted = numbers_in(raw)
    assert "52000000" in extracted


def test_numbers_in_multiple():
    """Verifies that multiple numbers in a single text segment are all extracted."""
    raw = "Clause 3.2: 150% of advertised value i.e. Rs. 50,00,000 over 3 years"
    extracted = numbers_in(raw)
    assert extracted == {"3.2", "150", "5000000", "3"}


def test_numbers_in_decimal():
    """Verifies that decimal points are preserved when extracting numbers."""
    raw = "Value: Rs. 78,39,23,735.01 and liquidity ratio 62.4"
    extracted = numbers_in(raw)
    assert "783923735.01" in extracted
    assert "62.4" in extracted


def test_numbers_in_no_numbers():
    """Verifies that text without numeric values returns an empty set."""
    assert numbers_in("Chartered Accountant Certificate attached") == set()
    assert numbers_in("") == set()
    assert numbers_in(None) == set()


# ==============================================================================
# 4. normalize_indian_amount() TESTS
# ==============================================================================

def test_normalize_lakhs():
    """Verifies that lakh expressions (e.g. '62.4 Lakhs') normalize to 6240000.0 INR."""
    assert normalize_indian_amount("62.4 Lakhs") == 6240000.0
    assert normalize_indian_amount("62.4 Lacs") == 6240000.0
    assert normalize_indian_amount("62.4 lac") == 6240000.0


def test_normalize_crores():
    """Verifies that crore expressions with 'Cr' (e.g. '2.5 Cr') normalize to 25000000.0 INR."""
    assert normalize_indian_amount("2.5 Cr") == 25000000.0
    assert normalize_indian_amount("2.5 cr.") == 25000000.0


def test_normalize_crores_full():
    """Verifies that full word 'Crores' (e.g. '2.5 Crores') normalizes to 25000000.0 INR."""
    assert normalize_indian_amount("2.5 Crores") == 25000000.0
    assert normalize_indian_amount("1 Crore") == 10000000.0


def test_normalize_plain_rupees():
    """Verifies that plain rupee strings with Indian comma formatting normalize to float INR."""
    assert normalize_indian_amount("Rs. 5,20,00,000") == 52000000.0
    assert normalize_indian_amount("Rs. 1,23,45,678.90") == 12345678.90


def test_normalize_with_symbol():
    """Verifies that amounts with currency symbol '₹' and '/-' normalize correctly."""
    assert normalize_indian_amount("₹ 50,000") == 50000.0
    assert normalize_indian_amount("₹50,000/-") == 50000.0


def test_normalize_unparseable():
    """Verifies that unparseable or non-numeric strings return None."""
    assert normalize_indian_amount("N/A") is None
    assert normalize_indian_amount("NA") is None
    assert normalize_indian_amount("None") is None
    assert normalize_indian_amount("") is None
    assert normalize_indian_amount("Not Applicable") is None
    assert normalize_indian_amount(None) is None


def test_normalize_thousands():
    """Verifies that thousand amounts normalize with multiplier 1,000."""
    assert normalize_indian_amount("50 Thousand") == 50000.0
    assert normalize_indian_amount("INR 10 Thousands") == 10000.0


# ==============================================================================
# 5. is_numeric_grounded() TESTS
# ==============================================================================

def test_numeric_grounded_exact():
    """Verifies that an extracted numeric value matching the quote directly returns True."""
    quote = "Total contract value awarded is Rs. 50,00,000."
    assert is_numeric_grounded(5000000.0, quote) is True


def test_numeric_grounded_lakh_conversion():
    """Verifies that 6240000.0 matches quote containing '62.4 Lakhs' via unit conversion."""
    quote = "Average annual turnover of the bidder: 62.4 Lakhs."
    assert is_numeric_grounded(6240000.0, quote) is True


def test_numeric_grounded_crore_conversion():
    """Verifies that 25000000.0 matches quote containing '2.5 Cr' via unit conversion."""
    quote = "Liquid assets available: 2.5 Cr as certified by Bank."
    assert is_numeric_grounded(25000000.0, quote) is True


def test_numeric_grounded_wrong_value():
    """Verifies that an extracted value not present in the quote returns False."""
    quote = "Annual turnover: Rs. 10,00,000 in FY 2023-24."
    assert is_numeric_grounded(5000000.0, quote) is False


# ==============================================================================
# 6. validate_udyam_format() TESTS
# ==============================================================================

def test_udyam_valid():
    """Verifies that standard valid UDYAM numbers pass validation."""
    assert validate_udyam_format("UDYAM-MH-01-0012345") is True
    assert validate_udyam_format("UDYAM-DL-05-1234567") is True


def test_udyam_invalid_prefix():
    """Verifies that UDYAM numbers with an invalid prefix (e.g. MSME, SSI) fail validation."""
    assert validate_udyam_format("MSME-MH-01-0012345") is False
    assert validate_udyam_format("SSI-DL-05-1234567") is False


def test_udyam_wrong_length():
    """Verifies that UDYAM numbers with too few or too many digits fail validation."""
    # 6 digits at end instead of 7
    assert validate_udyam_format("UDYAM-MH-01-001234") is False
    # 8 digits at end instead of 7
    assert validate_udyam_format("UDYAM-MH-01-00123456") is False
    # 1 digit district code
    assert validate_udyam_format("UDYAM-MH-1-0012345") is False


def test_udyam_case_insensitive():
    """Verifies that lowercase or mixed-case UDYAM numbers pass validation."""
    assert validate_udyam_format("udyam-mh-01-0012345") is True
    assert validate_udyam_format("Udyam-GJ-02-0098765") is True


# ==============================================================================
# 7. validate_udin_format() TESTS
# ==============================================================================

def test_udin_valid_18chars():
    """Verifies that 18-character alphanumeric ICAI UDINs pass validation."""
    assert validate_udin_format("21123456AAAA123456") is True
    assert validate_udin_format("12345678901234AB12") is True


def test_udin_too_short():
    """Verifies that UDIN strings shorter than 18 characters fail validation."""
    assert validate_udin_format("12345678901234567") is False  # 17 chars
    assert validate_udin_format("") is False
    assert validate_udin_format(None) is False


def test_udin_too_long():
    """Verifies that UDIN strings longer than 18 characters fail validation."""
    assert validate_udin_format("1234567890123456789") is False  # 19 chars


def test_udin_special_chars():
    """Verifies that UDIN strings containing special characters or punctuation fail validation."""
    assert validate_udin_format("12345678901234567-") is False
    assert validate_udin_format("21123456@AAA123456") is False
    assert validate_udin_format("UDIN 1234567890123") is False


# ==============================================================================
# 8. ground_field() TESTS
# ==============================================================================

def test_ground_field_grounded():
    """Verifies full grounding pipeline when quote is grounded on page and numeric value matches quote."""
    page_text = "Turnover Requirement (T-1): Rs. 5,20,00,000 as per audited balance sheet."
    quote = "Turnover Requirement (T-1): Rs. 5,20,00,000"
    field_value = 52000000.0

    result = ground_field(field_value=field_value, quote=quote, page_text=page_text, page_num=2)
    assert result["grounded"] is True
    assert result["reason_code"] is None
    assert result["confidence_adjustment"] == 0.0


def test_ground_field_ungrounded_quote():
    """Verifies full grounding pipeline returns QUOTE_NOT_GROUNDED when quote is not on page."""
    page_text = "General conditions of contract: Section A."
    quote = "Turnover requirement of Rs. 10 Crore"
    field_value = 100000000.0

    result = ground_field(field_value=field_value, quote=quote, page_text=page_text, page_num=1)
    assert result["grounded"] is False
    assert result["reason_code"] == "QUOTE_NOT_GROUNDED"
    assert result["confidence_adjustment"] < 0.0


def test_ground_field_numeric_mismatch():
    """Verifies full grounding pipeline returns NUMERIC_MISMATCH when quote exists on page but numeric value does not match quote."""
    page_text = "Turnover Requirement: Rs. 5,20,00,000 as per audited balance sheet."
    quote = "Turnover Requirement: Rs. 5,20,00,000"
    # Extracted value does not match 5.2 Crore
    field_value = 10000000.0

    result = ground_field(field_value=field_value, quote=quote, page_text=page_text, page_num=1)
    assert result["grounded"] is False
    assert result["reason_code"] == "NUMERIC_MISMATCH"
    assert result["confidence_adjustment"] < 0.0


def test_ground_field_non_numeric_grounded():
    """Verifies full grounding pipeline for string fields (e.g. entity name) succeeds when quote is grounded."""
    page_text = "Eligible entities: Railway PSUs and Joint Ventures."
    quote = "Railway PSUs"
    field_value = "Railway PSUs"

    result = ground_field(field_value=field_value, quote=quote, page_text=page_text, page_num=1)
    assert result["grounded"] is True
    assert result["reason_code"] is None
    assert result["confidence_adjustment"] == 0.0


def test_ground_field_boolean_not_treated_as_numeric():
    """Verifies that boolean values (True/False) are not treated as numbers (1/0) during numeric grounding."""
    page_text = "The undertaking is hereby signed and verified."
    quote = "signed and verified"
    field_value = True

    result = ground_field(field_value=field_value, quote=quote, page_text=page_text, page_num=1)
    assert result["grounded"] is True
    assert result["reason_code"] is None
    assert result["confidence_adjustment"] == 0.0
