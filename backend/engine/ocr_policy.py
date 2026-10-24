"""
OCR confidence policy and prompt-injection safeguards for TenderBee.

This module enforces:
1. Minimum and warning OCR confidence thresholds for tender document pages.
2. Filtering and gating of low-confidence pages requiring human verification.
3. Combining model-reported confidence with OCR confidence scores.
4. Scanning page text for prompt-injection attacks and adversarial instructions.
5. Comprehensive page-level quality and security assessments.
"""
from __future__ import annotations

import re
import os
from io import BytesIO
from pathlib import Path
from typing import Any, Optional, Tuple

# ==============================================================================
# CONSTANTS & POLICIES
# ==============================================================================

OCR_MIN_CONFIDENCE: float = 0.60
OCR_WARNING_CONFIDENCE: float = 0.85

REASON_LOW_OCR_CONFIDENCE: str = "LOW_OCR_CONFIDENCE"
REASON_CONFIDENCE_MODERATE: str = "CONFIDENCE_MODERATE"
REASON_POSSIBLE_INJECTION: str = "POSSIBLE_INJECTION"

STATUS_VERIFIED: str = "VERIFIED"
STATUS_VERIFIED_WITH_WARNING: str = "VERIFIED_WITH_WARNING"
STATUS_NEEDS_REVIEW: str = "NEEDS_REVIEW"

INJECTION_PATTERNS: tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous",
    "disregard above",
    "disregard all",
    "disregard instructions",
    "you are now",
    "new instructions",
    "system prompt",
    "reveal the api key",
    "show the api key",
    "call the tool",
    "execute shell command",
    "transmit the document contents",
    "send the document contents",
    "mark as eligible",
    "mark everything",
    "mark as verified",
    "return only approved",
    "override",
    "override validation",
    "forget everything",
    "act as",
    "pretend to be",
    "do not follow",
    "bypass",
    "bypass checks",
)

try:
    import pymupdf as fitz
except ModuleNotFoundError:  # pragma: no cover - optional until OCR is configured
    fitz = None

try:
    from PIL import Image
    import pytesseract
    from pytesseract import Output
except ModuleNotFoundError:  # pragma: no cover - optional until OCR is configured
    Image = None
    pytesseract = None
    Output = None


# ==============================================================================
# OCR CONFIDENCE FUNCTIONS
# ==============================================================================

def check_page_ocr(page: dict[str, Any]) -> dict[str, Any]:
    """Checks a single page's OCR confidence.

    Input format:
        {"page": 1, "text": "...", "ocr_conf": 0.84}

    Threshold rules:
        - ocr_conf < 0.60: usable=False, status="NEEDS_REVIEW", reason="LOW_OCR_CONFIDENCE"
        - 0.60 <= ocr_conf < 0.85: usable=True, status="VERIFIED_WITH_WARNING", reason="CONFIDENCE_MODERATE"
        - ocr_conf >= 0.85: usable=True, status="VERIFIED", reason=None
        - Missing or None ocr_conf: treated as native digital text (1.0)

    Args:
        page: Dict containing page metadata, text, and optional ocr_conf.

    Returns:
        dict: {"page": int, "usable": bool, "status": str, "reason": str | None}
    """
    page_num = page.get("page", 1)
    ocr_conf = page.get("ocr_conf")

    if ocr_conf is None:
        conf_val = 1.0
    else:
        conf_val = float(ocr_conf)

    if conf_val < OCR_MIN_CONFIDENCE:
        return {
            "page": page_num,
            "usable": False,
            "status": STATUS_NEEDS_REVIEW,
            "reason": REASON_LOW_OCR_CONFIDENCE,
        }
    elif conf_val < OCR_WARNING_CONFIDENCE:
        return {
            "page": page_num,
            "usable": True,
            "status": STATUS_VERIFIED_WITH_WARNING,
            "reason": REASON_CONFIDENCE_MODERATE,
        }
    else:
        return {
            "page": page_num,
            "usable": True,
            "status": STATUS_VERIFIED,
            "reason": None,
        }


def filter_pages(pages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Splits pages into usable and unusable based on OCR confidence.

    Args:
        pages: List of page dictionaries, each optionally having "ocr_conf".

    Returns:
        tuple[list[dict], list[dict]]: (usable_pages, review_pages)
            - usable_pages: pages with ocr_conf >= OCR_MIN_CONFIDENCE (0.60)
            - review_pages: pages with ocr_conf < OCR_MIN_CONFIDENCE (0.60)
    """
    usable_pages: list[dict[str, Any]] = []
    review_pages: list[dict[str, Any]] = []

    for page in pages:
        ocr_conf = page.get("ocr_conf")
        if ocr_conf is None:
            conf_val = 1.0
        else:
            conf_val = float(ocr_conf)

        if conf_val >= OCR_MIN_CONFIDENCE:
            usable_pages.append(page)
        else:
            review_pages.append(page)

    return usable_pages, review_pages


def get_combined_confidence(
    model_confidence: float,
    ocr_confidence: float | None = 1.0,
) -> float:
    """Combines model-reported and OCR confidence.

    Digital text layers count as 1.0 for OCR.

    Args:
        model_confidence: Extraction confidence reported by the model (0.0 to 1.0).
        ocr_confidence: Page OCR confidence (0.0 to 1.0) or None for digital text.

    Returns:
        float: min(model_confidence, ocr_confidence)
    """
    if ocr_confidence is None:
        ocr_conf_val = 1.0
    else:
        ocr_conf_val = float(ocr_confidence)
    return min(float(model_confidence), ocr_conf_val)


def confidence_status(combined: float) -> str:
    """Returns the verdict status based on combined confidence score.

    Threshold rules:
        - >= 0.85: "VERIFIED"
        - >= 0.60: "VERIFIED_WITH_WARNING"
        - < 0.60:  "NEEDS_REVIEW"

    Args:
        combined: Combined confidence score (0.0 to 1.0).

    Returns:
        str: "VERIFIED", "VERIFIED_WITH_WARNING", or "NEEDS_REVIEW"
    """
    combined_val = float(combined)
    if combined_val >= OCR_WARNING_CONFIDENCE:
        return STATUS_VERIFIED
    elif combined_val >= OCR_MIN_CONFIDENCE:
        return STATUS_VERIFIED_WITH_WARNING
    else:
        return STATUS_NEEDS_REVIEW


# ==============================================================================
# PROMPT INJECTION SAFEGUARDS
# ==============================================================================

def scan_for_injection(text: str) -> dict[str, Any]:
    """Scans page text for possible prompt-injection patterns.

    Case-insensitive matching with whole-word boundary validation to avoid
    false positives on legitimate domain terms (e.g., 'impact assessment').

    Risk levels:
        - "NONE": 0 patterns detected
        - "LOW": 1 pattern detected
        - "MEDIUM": 2-3 patterns detected
        - "HIGH": 4+ patterns detected

    Args:
        text: Page text content to scan.

    Returns:
        dict: {
            "suspicious": bool,
            "patterns_found": list[str],
            "risk_level": str
        }
    """
    if not text:
        return {
            "suspicious": False,
            "patterns_found": [],
            "risk_level": "NONE",
        }

    patterns_found: list[str] = []
    for pattern in INJECTION_PATTERNS:
        # Match pattern with flexible whitespace between words and word boundaries
        words = pattern.split()
        pattern_regex = r"\s+".join(re.escape(w) for w in words)
        regex = rf"\b{pattern_regex}\b"
        if re.search(regex, text, re.IGNORECASE):
            patterns_found.append(pattern)

    count = len(patterns_found)
    if count == 0:
        risk_level = "NONE"
        suspicious = False
    elif count == 1:
        risk_level = "LOW"
        suspicious = True
    elif 2 <= count <= 3:
        risk_level = "MEDIUM"
        suspicious = True
    else:
        risk_level = "HIGH"
        suspicious = True

    return {
        "suspicious": suspicious,
        "patterns_found": patterns_found,
        "risk_level": risk_level,
    }


# ==============================================================================
# UNIFIED PAGE ASSESSMENT
# ==============================================================================

def assess_page(page: dict[str, Any]) -> dict[str, Any]:
    """Full page assessment combining OCR confidence and injection scanning.

    Input format:
        {"page": 1, "text": "...", "ocr_conf": 0.84}

    Rules:
        - usable is False if OCR fails (< 0.60) OR injection risk is HIGH.
        - status is "NEEDS_REVIEW" if not usable or suspicious injection detected.
        - status is "VERIFIED_WITH_WARNING" if OCR is moderate [0.60, 0.85).
        - status is "VERIFIED" if OCR is high (>= 0.85) and no injection detected.
        - reasons collects applicable diagnostic reasons:
            - "LOW_OCR_CONFIDENCE"
            - "CONFIDENCE_MODERATE"
            - "POSSIBLE_INJECTION"

    Args:
        page: Dict containing page number, text, and optional ocr_conf.

    Returns:
        dict: {
            "page": int,
            "ocr_check": dict,
            "injection_check": dict,
            "usable": bool,
            "status": str,
            "reasons": list[str]
        }
    """
    page_num = page.get("page", 1)
    ocr_result = check_page_ocr(page)
    text = str(page.get("text", "") or "")
    injection_result = scan_for_injection(text)

    reasons: list[str] = []
    if ocr_result.get("reason"):
        reasons.append(ocr_result["reason"])

    if injection_result.get("suspicious"):
        reasons.append(REASON_POSSIBLE_INJECTION)

    # usable: False if OCR fails OR injection risk is HIGH
    ocr_usable = ocr_result.get("usable", True)
    injection_high = injection_result.get("risk_level") == "HIGH"
    usable = bool(ocr_usable and not injection_high)

    # Determine status
    if not usable or injection_result.get("suspicious"):
        status = STATUS_NEEDS_REVIEW
    elif ocr_result.get("status") == STATUS_VERIFIED_WITH_WARNING:
        status = STATUS_VERIFIED_WITH_WARNING
    else:
        status = STATUS_VERIFIED

    return {
        "page": page_num,
        "ocr_check": ocr_result,
        "injection_check": injection_result,
        "usable": usable,
        "status": status,
        "reasons": reasons,
    }


class OCRPolicy:
    """Scanned-page OCR execution policy and confidence calculation."""

    @staticmethod
    def ocr_page(
        pdf_bytes: bytes,
        page_index: int,
        language: str = "eng",
    ) -> Tuple[str, Optional[float]]:
        if fitz is None or Image is None or pytesseract is None or Output is None:
            raise ModuleNotFoundError(
                "Scanned PDF OCR requires PyMuPDF, Pillow, pytesseract, and the Tesseract OCR executable."
            )
        if not pdf_bytes.startswith(b"%PDF-"):
            raise ValueError("Uploaded file is not a valid PDF.")
        if page_index < 0:
            raise ValueError("OCR page index must be zero or greater.")
        if not re.fullmatch(r"[A-Za-z0-9_+]+", language):
            raise ValueError("OCR language must contain only letters, numbers, underscores, and plus signs.")

        document = fitz.open(stream=pdf_bytes, filetype="pdf")
        try:
            if page_index >= len(document):
                raise ValueError("OCR page index is outside the PDF page range.")
            configured_tesseract = os.getenv("TESSERACT_CMD")
            if configured_tesseract:
                pytesseract.pytesseract.tesseract_cmd = configured_tesseract
            elif os.name == "nt":
                for candidate in (
                    Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
                    Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
                ):
                    if candidate.is_file():
                        pytesseract.pytesseract.tesseract_cmd = str(candidate)
                        break
            page = document.load_page(page_index)
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(BytesIO(pixmap.tobytes("png")))
            data = pytesseract.image_to_data(
                image,
                lang=language,
                output_type=Output.DICT,
                timeout=30,
            )
            text = pytesseract.image_to_string(image, lang=language, timeout=30)
        finally:
            document.close()

        confidences = []
        for word, confidence in zip(data["text"], data["conf"]):
            try:
                score = float(confidence)
            except (TypeError, ValueError):
                continue
            if word.strip() and score >= 0:
                confidences.append(score / 100.0)
        average_confidence = (
            round(sum(confidences) / len(confidences), 3) if confidences else 0.0
        )
        from backend.engine.grounding import DocumentGroundingPolicy

        return DocumentGroundingPolicy.sanitize_page_text(text), average_confidence

    @staticmethod
    def ocr_page_text(
        pdf_bytes: bytes,
        page_index: int,
        language: str = "eng",
    ) -> Tuple[str, Optional[float]]:
        return OCRPolicy.ocr_page(pdf_bytes, page_index, language)
