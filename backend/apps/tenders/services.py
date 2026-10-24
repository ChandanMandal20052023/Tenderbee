"""
Tender Intake & Rule-Pack Drafting Service.
Coordinates PDF extraction, web scraping, tiered storage persistence, and translating
tender clauses into versioned, human-confirmable RulePack objects.
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.services.scraper import UniversalTenderScraper
from backend.services.storage import TenderStorage
from backend.services.tinyfish import BidEasyScraper
from backend.engine.parser import TenderPDFExtractor
from backend.engine.schema import (
    DocumentType,
    ReferenceDates,
    Rule,
    RulePack,
    RuleSource,
    RuleStatus,
    RuleType,
    TenderPDFExtractionResult,
)


class TenderService:
    def __init__(
        self,
        scraper: Optional[Any] = None,
        storage: Optional[TenderStorage] = None,
        pdf_extractor: Optional[TenderPDFExtractor] = None,
    ):
        self.storage = storage or TenderStorage()
        self.scraper = scraper or UniversalTenderScraper(storage=self.storage)
        self.pdf_extractor = pdf_extractor or TenderPDFExtractor()

    def intake_tender(
        self,
        identifier: str,
        org_id: str = "org_default",
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Main web intake workflow:
        1. Ingests tender from URL or Tender Number via TinyFish / Cache.
        2. Automatically drafts an executable RulePack from extracted criteria.
        3. Persists draft RulePack into storage.
        4. Returns tender details and draft rules for human review.
        """
        scrape_result = self.scraper.fetch_tender(
            identifier=identifier, org_id=org_id, force_refresh=force_refresh
        )
        if not scrape_result.get("success"):
            return scrape_result

        tender_data = scrape_result["tender"]
        tender_number = tender_data.get("tender_number", "UNKNOWN")
        tender_id = f"tnd_{self.storage.compute_sha256(tender_number)[:12]}"

        # Parse submission deadline
        deadline_str = tender_data.get("submission_deadline")
        try:
            deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
        except Exception:
            deadline = datetime.now(timezone.utc)

        # Build proposed Rule list
        rules: List[Rule] = self._draft_rules_from_tender(tender_data)

        # Construct RulePack in DRAFT status
        rule_pack_dict = {
            "tender_id": tender_id,
            "version": 1,
            "status": RuleStatus.DRAFT.value,
            "rules": [r.model_dump() for r in rules],
        }
        rule_pack_hash = self.storage.compute_sha256(json.dumps(rule_pack_dict, sort_keys=True))
        rule_pack_id = f"rp_{rule_pack_hash[:16]}"

        rule_pack = RulePack(
            tender_id=tender_id,
            version=1,
            status=RuleStatus.DRAFT,
            content_hash=rule_pack_hash,
            reference_dates=ReferenceDates(submission_deadline=deadline),
            rules=rules,
        )

        # Persist RulePack in database
        self._save_rule_pack_to_db(rule_pack_id, rule_pack)

        return {
            "success": True,
            "is_cached": scrape_result.get("is_cached", False),
            "tender_id": tender_id,
            "tender_number": tender_number,
            "tender_title": tender_data.get("tender_title"),
            "buyer_name": tender_data.get("buyer_name"),
            "submission_deadline": deadline.isoformat(),
            "rule_pack_id": rule_pack_id,
            "rule_pack": rule_pack.model_dump(),
        }

    def intake_tender_pdf(
        self,
        pdf_path: str,
        org_id: str = "org_default",
        tender_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Production Tender PDF Intake:
        Extracts structured procurement parameters, eligibility clauses, and exact
        verbatim quotes with 1-indexed page citations, emitting a validated JSON schema output.
        """
        extraction: TenderPDFExtractionResult = self.pdf_extractor.extract_from_pdf(pdf_path)

        t_num = extraction.tender_number or f"TND-{self.storage.compute_sha256(str(pdf_path))[:8].upper()}"
        t_title = extraction.tender_title
        b_name = extraction.buyer_name or "Procuring Authority"
        deadline_str = extraction.submission_deadline or datetime.now(timezone.utc).isoformat()

        tender_data = extraction.model_dump()
        raw_text_summary = (
            f"Tender Notice PDF: {pdf_path}\n"
            f"Total Pages: {extraction.total_pages}\n"
            f"Digital Text Coverage: {extraction.digital_text_coverage}\n"
        )

        # Commit to tiered storage (SQLite + snapshot json file)
        storage_meta = self.storage.save_tender_and_snapshot(
            org_id=org_id,
            tender_number=t_num,
            tender_title=t_title,
            source_url=f"pdf_upload:{Path(pdf_path).name}",
            buyer_name=b_name,
            submission_deadline=deadline_str,
            estimated_value_inr=extraction.estimated_value_inr,
            extracted_data=tender_data,
            raw_text_payload=raw_text_summary,
            tender_id=tender_id,
        )

        # Draft compliance RulePack from extracted clauses
        tender_id = storage_meta["tender_id"]
        rules = self._draft_rules_from_tender(tender_data)

        rule_pack_dict = {
            "tender_id": tender_id,
            "version": 1,
            "status": RuleStatus.DRAFT.value,
            "rules": [r.model_dump() for r in rules],
        }
        rule_pack_hash = self.storage.compute_sha256(json.dumps(rule_pack_dict, sort_keys=True))
        rule_pack_id = f"rp_{rule_pack_hash[:16]}"

        try:
            deadline_dt = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
        except Exception:
            deadline_dt = datetime.now(timezone.utc)

        rule_pack = RulePack(
            tender_id=tender_id,
            version=1,
            status=RuleStatus.DRAFT,
            content_hash=rule_pack_hash,
            reference_dates=ReferenceDates(submission_deadline=deadline_dt),
            rules=rules,
        )
        self._save_rule_pack_to_db(rule_pack_id, rule_pack)

        return {
            "success": True,
            "is_cached": False,
            "tender_id": tender_id,
            "tender_number": t_num,
            "tender_title": t_title,
            "buyer_name": b_name,
            "submission_deadline": deadline_str,
            "estimated_value_inr": extraction.estimated_value_inr,
            "emd_amount_inr": extraction.emd_amount_inr,
            "contract_period": extraction.contract_period,
            "portal_website": extraction.portal_website,
            "rule_pack_id": rule_pack_id,
            "rule_pack": rule_pack.model_dump(),
            "extraction": extraction.model_dump(),
            "json_schema": extraction.get_json_schema(),
            "storage": storage_meta,
        }

    def _draft_rules_from_tender(self, tender_data: Dict[str, Any]) -> List[Rule]:
        """Translates scraped criteria and clauses into deterministic Rule models."""
        rules: List[Rule] = []
        clauses = tender_data.get("verbatim_clauses", [])
        eligibility = tender_data.get("eligibility_rules", {})
        mandatory_docs = tender_data.get("mandatory_documents", [])

        # Helper to find quote for clause type
        def find_quote(clause_type: str, default: str) -> RuleSource:
            for c in clauses:
                if c.get("clause_type") == clause_type:
                    return RuleSource(page=c.get("page", 1), quote=c.get("quote", default))
            return RuleSource(page=1, quote=default)

        # 1. Statutory Document Rules (Udyam & CA Certificate)
        if "udyam_registration" in mandatory_docs or eligibility.get("mse_exemption_applicable"):
            rules.append(
                Rule(
                    rule_id="R-DOC-UDYAM",
                    document_type=DocumentType.UDYAM_CERTIFICATE,
                    rule_type=RuleType.DOCUMENT_REQUIRED,
                    description="Valid Udyam Registration Certificate required for MSE eligibility / exemption.",
                    source=find_quote("mse_exemption", "Udyam Registration Certificate required."),
                    field="status",
                    operator="eq",
                    value="ACTIVE",
                )
            )

        if "ca_turnover_certificate" in mandatory_docs or eligibility.get("min_annual_turnover_inr"):
            rules.append(
                Rule(
                    rule_id="R-DOC-CA",
                    document_type=DocumentType.CA_TURNOVER_CERTIFICATE,
                    rule_type=RuleType.DOCUMENT_REQUIRED,
                    description="Chartered Accountant certified turnover balance sheet required.",
                    source=find_quote("turnover_requirement", "CA Turnover Certificate mandatory."),
                    field="status",
                    operator="eq",
                    value="SUBMITTED",
                )
            )

        # 2. Turnover Numeric Threshold Rule (T1)
        turnover_val = eligibility.get("min_annual_turnover_inr")
        if turnover_val:
            years = eligibility.get("turnover_years", 3)
            rules.append(
                Rule(
                    rule_id="R-TURNOVER-AVG3",
                    document_type=DocumentType.CA_TURNOVER_CERTIFICATE,
                    rule_type=RuleType.NUMERIC_THRESHOLD,
                    description=f"Average annual turnover over last {years} years must exceed ₹{turnover_val:,.2f}.",
                    source=find_quote("turnover_requirement", f"Minimum average turnover: INR {turnover_val}"),
                    field="average_turnover_inr",
                    operator="gte",
                    value=turnover_val,
                )
            )

        # 3. UDIN Mandatory Rule
        if eligibility.get("udin_mandatory"):
            rules.append(
                Rule(
                    rule_id="R-UDIN",
                    document_type=DocumentType.CA_TURNOVER_CERTIFICATE,
                    rule_type=RuleType.IDENTIFIER_PRESENT,
                    description="Chartered Accountant Unique Document Identification Number (UDIN) is mandatory.",
                    source=find_quote("udin_requirement", "UDIN must be mentioned on CA certificates."),
                    field="udin",
                    operator="present",
                    value=True,
                )
            )

        # 4. Liquidity Numeric Threshold Rule (T2)
        liquidity_val = eligibility.get("min_liquidity_inr")
        if liquidity_val:
            rules.append(
                Rule(
                    rule_id="R-LIQUIDITY",
                    document_type=DocumentType.BANKING_REFERENCE,
                    rule_type=RuleType.NUMERIC_THRESHOLD,
                    description=f"Working capital / liquidity facility must exceed ₹{liquidity_val:,.2f}.",
                    source=find_quote("liquidity_requirement", f"Minimum liquidity requirement: INR {liquidity_val}"),
                    field="available_credit_facility_inr",
                    operator="gte",
                    value=liquidity_val,
                )
            )

        # 5. Single Work Experience Contract Rule
        work_exp_val = eligibility.get("min_work_experience_inr")
        if work_exp_val:
            rules.append(
                Rule(
                    rule_id="R-WORK-EXP",
                    document_type=DocumentType.WORK_EXPERIENCE,
                    rule_type=RuleType.NUMERIC_THRESHOLD,
                    description=f"Single qualifying completed contract value must exceed ₹{work_exp_val:,.2f}.",
                    source=find_quote("work_experience_requirement", f"Single work experience: INR {work_exp_val}"),
                    field="contract_value_inr",
                    operator="gte",
                    value=work_exp_val,
                )
            )

        # 6. Truthfulness Undertaking (Annexure-I)
        rules.append(
            Rule(
                rule_id="R-DOC-ANNEXURE-I",
                document_type=DocumentType.TRUTHFULNESS_UNDERTAKING,
                rule_type=RuleType.DOCUMENT_REQUIRED,
                description="Signed Truthfulness & Non-Debarment Undertaking on letterhead (Annexure-I).",
                source=find_quote("truthfulness_undertaking", "Undertaking for truthfulness of documents."),
                field="signed",
                operator="eq",
                value=True,
            )
        )

        # 7. Entity Type Restriction (e.g. Railway PSUs)
        eligible_entities = eligibility.get("eligible_entity_types", [])
        if eligible_entities:
            rules.append(
                Rule(
                    rule_id="R-ENTITY-ELIGIBILITY",
                    document_type=DocumentType.UDYAM_CERTIFICATE,
                    rule_type=RuleType.FIELD_IN_SET,
                    description=f"Bidder entity type must belong to approved types: {', '.join(eligible_entities)}.",
                    source=find_quote("entity_eligibility_restriction", f"Eligible entities: {eligible_entities}"),
                    field="entity_type",
                    operator="in",
                    value=eligible_entities,
                )
            )

        return rules

    def _save_rule_pack_to_db(self, rule_pack_id: str, rule_pack: RulePack):
        """Persists the rule pack state in SQLite/PostgreSQL."""
        with sqlite3.connect(self.storage.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO rule_packs (
                    rule_pack_id, tender_id, version, status, content_hash, rules_json
                ) VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    rule_pack_id,
                    rule_pack.tender_id,
                    rule_pack.version,
                    rule_pack.status.value,
                    rule_pack.content_hash,
                    json.dumps([r.model_dump() for r in rule_pack.rules]),
                ),
            )
            conn.commit()

    def confirm_rule_pack(self, rule_pack_id: str, confirmed_by: str = "compliance_lead") -> Dict[str, Any]:
        """
        Transitions a RulePack from DRAFT to FROZEN.
        Calculates cryptographic hash and locks rules for assessment.
        """
        with sqlite3.connect(self.storage.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rule_packs WHERE rule_pack_id = ?", (rule_pack_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": f"RulePack '{rule_pack_id}' not found."}

            if row["status"] == RuleStatus.FROZEN.value:
                return {
                    "success": True,
                    "message": "RulePack already frozen.",
                    "rule_pack_id": rule_pack_id,
                    "status": RuleStatus.FROZEN.value,
                }

            rules = json.loads(row["rules_json"])
            now = datetime.now(timezone.utc).isoformat()

            # Hash the frozen rules payload
            frozen_content = {
                "rule_pack_id": rule_pack_id,
                "tender_id": row["tender_id"],
                "version": row["version"],
                "confirmed_by": confirmed_by,
                "confirmed_at": now,
                "rules": rules,
            }
            frozen_hash = self.storage.compute_sha256(json.dumps(frozen_content, sort_keys=True))

            cursor.execute(
                """
                UPDATE rule_packs SET
                    status = ?,
                    content_hash = ?,
                    confirmed_by = ?,
                    confirmed_at = ?
                WHERE rule_pack_id = ?
            """,
                (RuleStatus.FROZEN.value, frozen_hash, confirmed_by, now, rule_pack_id),
            )
            conn.commit()

            return {
                "success": True,
                "rule_pack_id": rule_pack_id,
                "tender_id": row["tender_id"],
                "status": RuleStatus.FROZEN.value,
                "content_hash": frozen_hash,
                "confirmed_by": confirmed_by,
                "confirmed_at": now,
                "rule_count": len(rules),
            }

    def get_rule_pack(self, rule_pack_id: str) -> Optional[RulePack]:
        """Retrieves and deserializes a RulePack by ID."""
        with sqlite3.connect(self.storage.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rule_packs WHERE rule_pack_id = ?", (rule_pack_id,))
            row = cursor.fetchone()
            if not row:
                return None

            rules_data = json.loads(row["rules_json"])
            rules = [Rule(**r) for r in rules_data]

            cursor.execute("SELECT submission_deadline FROM tenders WHERE tender_id = ?", (row["tender_id"],))
            t_row = cursor.fetchone()
            try:
                deadline = datetime.fromisoformat(t_row["submission_deadline"]) if t_row else datetime.now(timezone.utc)
            except Exception:
                deadline = datetime.now(timezone.utc)

            return RulePack(
                tender_id=row["tender_id"],
                version=row["version"],
                status=RuleStatus(row["status"]),
                content_hash=row["content_hash"],
                reference_dates=ReferenceDates(submission_deadline=deadline),
                rules=rules,
            )

    def get_rule_pack_by_tender_id(self, tender_id: str) -> Optional[RulePack]:
        """Retrieves and deserializes the active/draft RulePack for a tender."""
        with sqlite3.connect(self.storage.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT external_id FROM tenders WHERE tender_id = ?", (tender_id,))
            t_row = cursor.fetchone()
            ext_id = t_row["external_id"] if t_row else None
            alt_id = f"tnd_{self.storage.compute_sha256(ext_id)[:12]}" if ext_id else None

            cursor.execute(
                """SELECT rule_pack_id FROM rule_packs 
                   WHERE tender_id = ? OR (tender_id = ? AND ? IS NOT NULL)
                   ORDER BY version DESC LIMIT 1""",
                (tender_id, alt_id, alt_id),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return self.get_rule_pack(row["rule_pack_id"])

    def get_tender(self, identifier: str, mode: str = "skim") -> Optional[Dict[str, Any]]:
        """
        Retrieves tender details supporting both viewing modes:
        - 'skim': Fast summary of metadata (title, buyer, estimated value, EMD, tenure, deadline)
        - 'detailed': Parses the full PDF notice, extracts all verbatim clauses with page numbers, and returns draft rules.
        """
        from backend.apps.tenders.search import TenderSearchService
        return TenderSearchService(storage=self.storage).get_tender(identifier, mode=mode)

