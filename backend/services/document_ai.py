from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from pypdf import PdfReader
except ModuleNotFoundError:  # pragma: no cover - optional when PDF stack is unavailable
    PdfReader = None

from backend.engine.grounding import DocumentGroundingPolicy
from backend.engine.ocr_policy import OCRPolicy, assess_page


class DocumentAISafeExtractor:
    """Backward-compatible facade for the shared engine extraction policies."""

    sanitize_text = staticmethod(DocumentGroundingPolicy.sanitize_text)
    sanitize_page_text = staticmethod(DocumentGroundingPolicy.sanitize_page_text)
    detect_prompt_injection = staticmethod(DocumentGroundingPolicy.detect_prompt_injection)
    extract_document_facts = staticmethod(DocumentGroundingPolicy.extract_document_facts)
    _find_value = staticmethod(DocumentGroundingPolicy._find_value)

    @staticmethod
    def extract_from_pdf(pdf_path: Union[str, Path]) -> Dict[str, Any]:
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")
        return DocumentAISafeExtractor.extract_from_bytes(path.read_bytes())

    @staticmethod
    def extract_from_bytes(pdf_bytes: bytes, ocr_language: str = "eng") -> Dict[str, Any]:
        if not pdf_bytes.startswith(b"%PDF-"):
            raise ValueError("Uploaded file is not a valid PDF.")
        if PdfReader is None:
            raise ModuleNotFoundError("pypdf is required for PDF extraction")

        reader = PdfReader(BytesIO(pdf_bytes), strict=True)
        if len(reader.pages) > 500:
            raise ValueError("PDF exceeds the 500-page extraction limit.")
        pages: List[Tuple[int, str]] = []
        page_results: List[Dict[str, Any]] = []
        page_facts: List[Dict[str, Any]] = []
        for index, page in enumerate(reader.pages, start=1):
            text = DocumentGroundingPolicy.sanitize_page_text(page.extract_text() or "")
            ocr_confidence: Optional[float] = None
            ocr_used = len(text) < 40
            if ocr_used:
                try:
                    ocr_text, ocr_conf = DocumentAISafeExtractor._ocr_page(
                        pdf_bytes,
                        index - 1,
                        ocr_language,
                    )
                    if ocr_text:
                        text = ocr_text
                    ocr_confidence = ocr_conf
                except (ModuleNotFoundError, Exception):
                    pass
            page_assessment = assess_page({
                "page": index,
                "text": text,
                "ocr_conf": ocr_confidence,
            })
            pages.append((index, text))
            page_results.append({
                "page": index,
                "text": text,
                "is_scanned": ocr_used,
                "ocr_confidence": ocr_confidence,
                "ocr_status": page_assessment["status"],
                "needs_review": not page_assessment["usable"],
            })
            page_facts.append(
                DocumentGroundingPolicy.extract_document_facts(
                    text,
                    page_number=index,
                    confidence=ocr_confidence if ocr_confidence is not None else 1.0,
                )
            )

        facts = DocumentGroundingPolicy.extract_document_facts(
            "\n".join(text for _, text in pages)
        )
        for page_fact in page_facts:
            facts["fields"].update(page_fact["fields"])
            facts["field_evidence"].update(page_fact["field_evidence"])
            facts["grounded_quotes"].extend(page_fact["grounded_quotes"])
            if page_fact["document_type"] != "unknown":
                facts["document_type"] = page_fact["document_type"]
        facts["pages"] = page_results
        facts["ocr_used"] = any(page["is_scanned"] for page in page_results)
        facts["needs_review"] = (
            any(page["needs_review"] for page in page_results)
            or bool(facts["suspicious_prompt_patterns"])
        )
        return facts

    @staticmethod
    def _ocr_page(
        pdf_bytes: bytes,
        page_index: int,
        language: str,
    ) -> Tuple[str, Optional[float]]:
        return OCRPolicy.ocr_page(pdf_bytes, page_index, language)

    @staticmethod
    def ocr_page_text(
        pdf_bytes: bytes,
        page_index: int,
        language: str = "eng",
    ) -> Tuple[str, Optional[float]]:
        return OCRPolicy.ocr_page_text(pdf_bytes, page_index, language)
