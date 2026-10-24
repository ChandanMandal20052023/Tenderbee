import json
import subprocess
import sys
from pathlib import Path

import fitz

from scripts.extract_documents import main, run_document_extraction, run_extraction

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def make_pdf(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    content = document.tobytes()
    document.close()
    return content


def test_cli_extracts_in_schema_shape_without_applying_constraints(tmp_path, capsys):
    schema_path = tmp_path / "extraction.schema.json"
    application = tmp_path / "udyam.pdf"
    output = tmp_path / "extracted.json"
    evidence_output = tmp_path / "evidence.json"
    schema_path.write_text(
        json.dumps({
            "type": "object",
            "properties": {
                "udyam_certificate": {
                    "type": "object",
                    "x-document-type": "udyam_certificate",
                    "properties": {
                        "status": {
                            "type": "string",
                            "const": "INACTIVE",
                            "description": "Extract the status; do not decide compliance.",
                        },
                        "company_name": {
                            "type": "string",
                            "x-extract-label": "Enterprise Name",
                        },
                    },
                }
            },
        }),
        encoding="utf-8",
    )
    application.write_bytes(make_pdf(
        "Udyam Registration Number: UDYAM-MH-01-0012345\n"
        "Udyam Certificate Status: ACTIVE\n"
        "Enterprise Name: Example Works Private Limited"
    ))

    exit_code = main([
        "--schema", str(schema_path),
        "--application", str(application),
        "--output", str(output),
        "--evidence", str(evidence_output),
    ])

    captured = capsys.readouterr()
    assert exit_code == 0
    extracted = json.loads(output.read_text(encoding="utf-8"))
    assert extracted == {
        "udyam_certificate": {
            "status": "ACTIVE",
            "company_name": "Example Works Private Limited",
        }
    }
    assert json.loads(captured.out) == extracted
    evidence = json.loads(evidence_output.read_text(encoding="utf-8"))
    assert evidence["field_evidence"]["udyam_certificate"]["status"]["page"] == 1
    assert "Certificate Status: ACTIVE" in evidence["field_evidence"]["udyam_certificate"]["status"]["quote"]
    assert "assessment" not in evidence


def test_cli_preserves_partial_extraction_and_does_not_invent_unknown_fields(tmp_path):
    schema_path = tmp_path / "extraction.schema.json"
    application = tmp_path / "other.pdf"
    schema_path.write_text(
        json.dumps({
            "type": "object",
            "properties": {
                "other": {
                    "type": "object",
                    "x-document-type": "other",
                    "properties": {
                        "registration_id": {
                            "type": "string",
                            "x-extract-label": "Registration ID",
                        },
                        "owner_name": {
                            "type": "string",
                            "x-extract-label": "Owner Name",
                        },
                    },
                }
            },
        }),
        encoding="utf-8",
    )
    application.write_bytes(make_pdf(
        "Registration ID: REG-2026-007\n"
        "This bidder document contains additional identification text for extraction."
    ))

    report = run_extraction(schema_path, [f"other={application}"])

    assert report["extracted_data"] == {"other": {"registration_id": "REG-2026-007"}}
    assert "owner_name" not in report["extracted_data"]["other"]
    assert report["field_evidence"]["other"]["registration_id"]["page"] == 1


def test_sample_schema_extracts_known_document_fields(tmp_path):
    schema_path = REPOSITORY_ROOT / "samples" / "application_extraction.schema.json"
    udyam_pdf = tmp_path / "udyam.pdf"
    turnover_pdf = tmp_path / "turnover.pdf"
    udyam_pdf.write_bytes(make_pdf(
        "Udyam Registration Number: UDYAM-MH-01-0012345\n"
        "Udyam Certificate Status: ACTIVE\n"
        "Entity Type: Railway PSUs"
    ))
    turnover_pdf.write_bytes(make_pdf(
        "Chartered Accountant Turnover Certificate\n"
        "UDIN: ABC12345XYZ\n"
        "Average Annual Turnover: Rs. 85,00,00,000.00"
    ))

    report = run_extraction(schema_path, [
        str(udyam_pdf),
        f"ca_turnover_certificate={turnover_pdf}",
    ])

    assert report["extracted_data"]["udyam_certificate"]["status"] == "ACTIVE"
    assert report["extracted_data"]["udyam_certificate"]["entity_type"] == "Railway PSUs"
    assert report["extracted_data"]["ca_turnover_certificate"]["average_turnover_inr"] == 850000000.0
    assert report["extracted_data"]["ca_turnover_certificate"]["udin"] == "ABC12345XYZ"


def test_plain_pdf_argument_extracts_full_page_text_without_schema(tmp_path, capsys):
    tender_pdf = tmp_path / "Tender in Business.pdf"
    output_path = tmp_path / "extracted.json"
    expected_text = (
        "Invitation for Tender: Business Support Services\n"
        "The bidder shall submit a valid registration certificate and audited accounts."
    )
    tender_pdf.write_bytes(make_pdf(expected_text))

    exit_code = main([str(tender_pdf), "--output", str(output_path)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "readiness" not in captured.out.lower()
    result = json.loads(output_path.read_text(encoding="utf-8"))
    assert result["documents"][0]["pages"][0]["text"] == expected_text
    assert result["documents"][0]["file"] == "Tender in Business.pdf"
    assert result["documents"][0]["sha256"]
    assert run_document_extraction([tender_pdf])["documents"][0]["ocr_used"] is False


def test_cli_script_runs_from_repository_root():
    result = subprocess.run(
        [sys.executable, "scripts/extract_documents.py", "--help"],
        cwd=REPOSITORY_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--schema SCHEMA" in result.stdout
    assert "ModuleNotFoundError" not in result.stderr


def test_legacy_cli_wrapper_runs_from_backend_directory():
    result = subprocess.run(
        [sys.executable, "demo_cli.py", "--help"],
        cwd=REPOSITORY_ROOT / "backend",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--schema SCHEMA" in result.stdout
    assert "ModuleNotFoundError" not in result.stderr
