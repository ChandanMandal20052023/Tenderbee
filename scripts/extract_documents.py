from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

# Support direct execution from the repository root and from another working directory.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pypdf.errors import PdfReadError, PdfStreamError

from backend.engine.schema import DocumentType
from backend.services.document_ai import DocumentAISafeExtractor


MAX_PDF_BYTES = 20 * 1024 * 1024
MAX_APPLICATIONS = 20
MAX_TOTAL_PAGES = 500
_DOCUMENT_SCHEMA_ANNOTATIONS = {
    "$comment",
    "title",
    "description",
    "default",
    "examples",
    "type",
    "properties",
    "required",
    "additionalProperties",
    "x-document-type",
}
_FIELD_SCHEMA_ANNOTATIONS = {
    "$comment",
    "title",
    "description",
    "default",
    "examples",
    "type",
    "const",
    "enum",
    "minimum",
    "exclusiveMinimum",
    "maximum",
    "exclusiveMaximum",
    "multipleOf",
    "minLength",
    "maxLength",
    "pattern",
    "format",
    "x-extract-field",
    "x-extract-label",
}
_ROOT_SCHEMA_ANNOTATIONS = {
    "$schema",
    "$id",
    "$comment",
    "title",
    "description",
    "default",
    "examples",
    "type",
    "properties",
    "required",
    "additionalProperties",
}
_LABEL_ALIASES = {
    "average_turnover_inr": ("average annual turnover", "average turnover"),
    "available_credit_facility_inr": ("working capital", "credit facility"),
    "entity_type": ("entity type", "bidder category", "category"),
    "udyam_registration_number": ("udyam registration number", "udyam number"),
    "udin": ("udin",),
    "status": ("certificate status", "status"),
}


def _schema_properties(schema: dict[str, Any], name: str) -> dict[str, Any]:
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        raise ValueError(f"'{name}.properties' must be an object.")
    return properties


def _validate_schema(schema: Any) -> dict[str, Any]:
    if not isinstance(schema, dict) or schema.get("type") != "object":
        raise ValueError("The extraction JSON Schema must describe an object.")
    properties = _schema_properties(schema, "root")
    if not properties:
        raise ValueError("The extraction schema must define document objects under 'properties'.")
    unsupported_root = set(schema) - _ROOT_SCHEMA_ANNOTATIONS
    if unsupported_root:
        raise ValueError(
            "Unsupported top-level schema keyword(s): " + ", ".join(sorted(unsupported_root))
        )
    if schema.get("additionalProperties", True) is not True:
        raise ValueError("additionalProperties schemas are not supported.")

    allowed_types = {item.value for item in DocumentType}
    for document_name, document_schema in properties.items():
        if not isinstance(document_schema, dict) or document_schema.get("type") != "object":
            raise ValueError(f"Document '{document_name}' must have type 'object'.")
        document_type = document_schema.get("x-document-type", document_name)
        if not isinstance(document_type, str) or document_type not in allowed_types:
            raise ValueError(
                f"'{document_name}' must use a supported document type or set x-document-type. "
                f"Supported types: {', '.join(sorted(allowed_types))}."
            )
        unsupported_document = set(document_schema) - _DOCUMENT_SCHEMA_ANNOTATIONS
        if unsupported_document:
            raise ValueError(
                f"Unsupported schema keyword(s) for document '{document_name}': "
                + ", ".join(sorted(unsupported_document))
            )
        if document_schema.get("additionalProperties", True) is not True:
            raise ValueError(f"additionalProperties schemas are not supported for '{document_name}'.")
        field_properties = _schema_properties(document_schema, document_name)
        for field_name, field_schema in field_properties.items():
            if not isinstance(field_schema, dict):
                raise ValueError(f"Schema for '{document_name}.{field_name}' must be an object.")
            unsupported_field = set(field_schema) - _FIELD_SCHEMA_ANNOTATIONS
            if unsupported_field:
                raise ValueError(
                    f"Unsupported schema keyword(s) for '{document_name}.{field_name}': "
                    + ", ".join(sorted(unsupported_field))
                )
            field_type = field_schema.get("type", "string")
            if field_type not in ("string", "number", "integer", "boolean"):
                raise ValueError(
                    f"'{document_name}.{field_name}' must be a scalar string, number, integer, or boolean."
                )
            if "x-extract-label" in field_schema and not isinstance(field_schema["x-extract-label"], str):
                raise ValueError(f"'{document_name}.{field_name}.x-extract-label' must be a string.")
            if "x-extract-field" in field_schema and not isinstance(field_schema["x-extract-field"], str):
                raise ValueError(f"'{document_name}.{field_name}.x-extract-field' must be a string.")
    return schema


def _parse_application_argument(argument: str) -> tuple[str | None, Path]:
    if "=" not in argument:
        return None, Path(argument)
    document_type, file_path = argument.split("=", 1)
    if not document_type or not file_path:
        raise ValueError("Use --application DOCUMENT_TYPE=PATH to assign a document type.")
    return document_type, Path(file_path)


def _coerce_value(raw_value: str, field_schema: dict[str, Any]) -> Any:
    field_type = field_schema.get("type", "string")
    value = raw_value.strip()
    if field_type == "string":
        return value
    if field_type in ("number", "integer"):
        numeric = re.search(r"[-+]?\d[\d,]*(?:\.\d+)?", value)
        if not numeric:
            return None
        number_text = numeric.group(0).replace(",", "")
        try:
            number = float(number_text)
        except ValueError:
            return None
        if field_type == "integer":
            return int(number) if number.is_integer() else None
        return number
    if field_type == "boolean":
        lowered = value.casefold()
        if lowered in ("true", "yes", "signed", "active", "present"):
            return True
        if lowered in ("false", "no", "unsigned", "inactive", "absent"):
            return False
    return None


def _extract_labeled_field(
    field_name: str,
    field_schema: dict[str, Any],
    page_text: str,
) -> dict[str, Any] | None:
    explicit_label = field_schema.get("x-extract-label")
    labels = [explicit_label] if explicit_label else list(
        _LABEL_ALIASES.get(field_schema.get("x-extract-field", field_name), ())
    )
    if not labels:
        labels = [re.sub(r"[_\-]+", " ", field_name)]
    for label in labels:
        if not label:
            continue
        match = re.search(
            rf"(?im)^\s*{re.escape(label)}\s*[:\-]\s*(.+?)\s*$",
            page_text,
        )
        if not match:
            continue
        raw_value = match.group(1).strip()
        value = _coerce_value(raw_value, field_schema)
        if value is None:
            continue
        return {
            "value": value,
            "page": None,
            "quote": match.group(0).strip(),
            "confidence": 1.0,
            "source": "text_label",
        }
    return None


def _get_field_evidence(
    field_name: str,
    field_schema: dict[str, Any],
    extraction: dict[str, Any],
) -> dict[str, Any] | None:
    extract_field = field_schema.get("x-extract-field", field_name)
    evidence = extraction.get("field_evidence", {}).get(extract_field)
    if evidence is not None:
        value = evidence.get("value")
        return {
            **evidence,
            "value": _coerce_value(str(value), field_schema),
            "source": "document_extractor",
        }
    for page in extraction.get("pages", []):
        evidence = _extract_labeled_field(field_name, field_schema, page.get("text", ""))
        if evidence is not None:
            evidence["page"] = page["page"]
            confidence = page.get("ocr_confidence")
            if confidence is not None:
                evidence["confidence"] = confidence
                evidence["source"] = "ocr_label"
            return evidence
    return None


def run_extraction(schema_path: Path, application_arguments: list[str]) -> dict[str, Any]:
    schema = _validate_schema(json.loads(schema_path.read_text(encoding="utf-8")))
    if not application_arguments:
        raise ValueError("Provide at least one --application PDF.")
    if len(application_arguments) > MAX_APPLICATIONS:
        raise ValueError(f"Provide no more than {MAX_APPLICATIONS} application PDFs.")

    document_schemas = schema["properties"]
    document_types = {
        document_schema.get("x-document-type", document_name): document_name
        for document_name, document_schema in document_schemas.items()
    }
    extracted_by_type: dict[str, list[dict[str, Any]]] = {}
    uploaded_files = []
    total_pages = 0
    for argument in application_arguments:
        explicit_type, file_path = _parse_application_argument(argument)
        if explicit_type and explicit_type not in document_types:
            raise ValueError(
                f"Document type '{explicit_type}' is not described in the schema. "
                "Assign PDFs only to a document type present in the supplied schema."
            )
        pdf_bytes = file_path.read_bytes()
        if not pdf_bytes or len(pdf_bytes) > MAX_PDF_BYTES:
            raise ValueError(f"PDF must be between 1 byte and 20 MiB: {file_path}")
        extraction = DocumentAISafeExtractor.extract_from_bytes(pdf_bytes)
        document_type = explicit_type or extraction["document_type"]
        if document_type not in document_types:
            raise ValueError(
                f"Could not identify a schema document type in '{file_path}'. "
                "Use --application DOCUMENT_TYPE=PATH to assign it explicitly."
            )
        extracted_by_type.setdefault(document_type, []).append(extraction)
        total_pages += len(extraction.get("pages", []))
        uploaded_files.append({
            "file": file_path.name,
            "document_type": document_type,
            "sha256": hashlib.sha256(pdf_bytes).hexdigest(),
            "pages": len(extraction.get("pages", [])),
            "ocr_used": extraction.get("ocr_used", False),
            "needs_review": extraction.get("needs_review", False),
            "suspicious_prompt_patterns": extraction.get("suspicious_prompt_patterns", []),
        })
        if total_pages > MAX_TOTAL_PAGES:
            raise ValueError(f"Application PDFs exceed the {MAX_TOTAL_PAGES}-page demo limit.")

    extracted_data: dict[str, Any] = {}
    field_evidence: dict[str, dict[str, Any]] = {}
    for document_type, document_name in document_types.items():
        document_schema = document_schemas[document_name]
        document_extractions = extracted_by_type.get(document_type)
        if not document_extractions:
            continue
        output_fields: dict[str, Any] = {}
        evidence_fields: dict[str, Any] = {}
        for field_name, field_schema in document_schema.get("properties", {}).items():
            evidence = None
            for extraction in document_extractions:
                evidence = _get_field_evidence(field_name, field_schema, extraction)
                if evidence is not None and evidence.get("value") is not None:
                    break
            if evidence is None or evidence.get("value") is None:
                continue
            output_fields[field_name] = evidence["value"]
            evidence_fields[field_name] = evidence
        extracted_data[document_name] = output_fields
        field_evidence[document_name] = evidence_fields

    return {
        "extracted_data": extracted_data,
        "field_evidence": field_evidence,
        "application_files": uploaded_files,
    }


def run_document_extraction(pdf_paths: list[Path]) -> dict[str, Any]:
    if not pdf_paths:
        raise ValueError("Provide at least one PDF path.")
    if len(pdf_paths) > MAX_APPLICATIONS:
        raise ValueError(f"Provide no more than {MAX_APPLICATIONS} PDFs.")

    documents = []
    total_pages = 0
    for file_path in pdf_paths:
        pdf_bytes = file_path.read_bytes()
        if not pdf_bytes or len(pdf_bytes) > MAX_PDF_BYTES:
            raise ValueError(f"PDF must be between 1 byte and 20 MiB: {file_path}")
        extraction = DocumentAISafeExtractor.extract_from_bytes(pdf_bytes)
        pages = extraction.get("pages", [])
        total_pages += len(pages)
        if total_pages > MAX_TOTAL_PAGES:
            raise ValueError(f"PDFs exceed the {MAX_TOTAL_PAGES}-page demo limit.")
        documents.append({
            "file": file_path.name,
            "sha256": hashlib.sha256(pdf_bytes).hexdigest(),
            "document_type": extraction.get("document_type", "unknown"),
            "fields": extraction.get("fields", {}),
            "field_evidence": extraction.get("field_evidence", {}),
            "pages": pages,
            "ocr_used": extraction.get("ocr_used", False),
            "needs_review": extraction.get("needs_review", False),
            "suspicious_prompt_patterns": extraction.get("suspicious_prompt_patterns", []),
        })
    return {"documents": documents}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Extract text and fields from PDFs. Supply PDF paths directly for full page text, "
            "or use --schema to shape field extraction."
        )
    )
    parser.add_argument(
        "--schema",
        dest="schema",
        type=Path,
        help="Optional JSON Schema describing the extraction output shape",
    )
    parser.add_argument(
        "--application",
        action="append",
        default=[],
        metavar="[DOCUMENT_TYPE=]PDF",
        help="PDF to extract with a schema (repeat; assign type if detection is ambiguous)",
    )
    parser.add_argument("pdfs", nargs="*", type=Path, help="PDF path(s) for full text/OCR extraction")
    parser.add_argument("--output", type=Path, help="Optional path for schema-shaped extracted JSON")
    parser.add_argument(
        "--evidence",
        type=Path,
        help="Optional path for page quotes and OCR metadata (schema mode)",
    )
    args = parser.parse_args(argv)

    try:
        if args.schema:
            application_arguments = list(args.application)
            application_arguments.extend(str(path) for path in args.pdfs)
            result = run_extraction(args.schema, application_arguments)
            output_data = result["extracted_data"]
            evidence_data = {
                "field_evidence": result["field_evidence"],
                "application_files": result["application_files"],
            }
        elif args.application:
            raise ValueError("Use positional PDF paths without --schema, or add --schema for --application.")
        else:
            result = run_document_extraction(args.pdfs)
            output_data = result
            evidence_data = None

        if args.evidence and evidence_data is None:
            raise ValueError("--evidence is only available with --schema.")
        output = json.dumps(output_data, indent=2)
        print(output)
        if args.output:
            args.output.write_text(output + "\n", encoding="utf-8")
        if args.evidence:
            args.evidence.write_text(
                json.dumps(
                    evidence_data,
                    indent=2,
                ) + "\n",
                encoding="utf-8",
            )
    except (
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        PdfReadError,
        PdfStreamError,
        EOFError,
        ValueError,
        RuntimeError,
        ModuleNotFoundError,
    ) as exc:
        print(f"Extraction failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
