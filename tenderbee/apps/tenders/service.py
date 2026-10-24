"""
Tender Intake & Rule-Pack Drafting Service.
Coordinates scraping, tiered storage persistence, and translating
tender clauses into versioned, human-confirmable RulePack objects.
"""
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
import sqlite3

from tenderbee.apps.tenders.scraper import BidEasyScraper
from tenderbee.apps.tenders.storage import TenderStorage
from tenderbee.core.schemas.enums import DocumentType, RuleStatus, RuleType
from tenderbee.core.schemas.rule_pack import (
    ReferenceDates,
    Rule,
    RulePack,
    RuleSource,
)


class TenderService:
    def __init__(self, scraper: Optional[BidEasyScraper] = None, storage: Optional[TenderStorage] = None):
        self.storage = storage or TenderStorage()
        self.scraper = scraper or BidEasyScraper(storage=self.storage)

    def intake_tender(self, identifier: str, org_id: str = "org_default", force_refresh: bool = False) -> Dict[str, Any]:
        """
        Main intake workflow:
        1. Ingests tender from URL or Tender Number via TinyFish / Cache.
        2. Automatically drafts an executable RulePack from extracted criteria.
        3. Persists draft RulePack into storage.
        4. Returns tender details and draft rules for human review.
        """
        scrape_result = self.scraper.fetch_tender(identifier=identifier, org_id=org_id, force_refresh=force_refresh)
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
            deadline = datetime.utcnow()

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
                    return RuleSource(page=1, quote=c.get("quote", default))
            return RuleSource(page=1, quote=default)

        # 1. Mandatory Document Rules
        if "udyam_certificate" in mandatory_docs or tender_data.get("mse_exemption_allowed"):
            rules.append(Rule(
                rule_id="R-DOC-UDYAM",
                type=RuleType.DOCUMENT_REQUIRED,
                mandatory=True,
                params={"document_type": DocumentType.UDYAM_CERTIFICATE.value},
                source=find_quote("udyam_requirement", "Bidder must upload valid Udyam certificate for MSE benefits.")
            ))

        if "ca_turnover_certificate" in mandatory_docs or eligibility.get("min_annual_turnover_inr"):
            rules.append(Rule(
                rule_id="R-DOC-CA",
                type=RuleType.DOCUMENT_REQUIRED,
                mandatory=True,
                params={"document_type": DocumentType.CA_TURNOVER_CERTIFICATE.value},
                source=find_quote("turnover_requirement", "Turnover must be certified by Chartered Accountant.")
            ))

        if "nsic_registration" in mandatory_docs:
            rules.append(Rule(
                rule_id="R-DOC-NSIC",
                type=RuleType.DOCUMENT_REQUIRED,
                mandatory=True,
                params={"document_type": DocumentType.NSIC_REGISTRATION.value},
                source=find_quote("nsic_requirement", "NSIC registration required for EMD exemption.")
            ))

        # 2. Turnover Numeric Threshold Rule
        turnover_inr = eligibility.get("min_annual_turnover_inr")
        if turnover_inr:
            n_years = eligibility.get("turnover_years", 3)
            rules.append(Rule(
                rule_id="R-TURNOVER-AVG3",
                type=RuleType.NUMERIC_THRESHOLD,
                mandatory=True,
                params={
                    "document_type": DocumentType.CA_TURNOVER_CERTIFICATE.value,
                    "field": "turnover_by_fy",
                    "aggregate": f"mean_last_{n_years}_completed_fy",
                    "n": n_years,
                    "operator": ">=",
                    "threshold_inr": float(turnover_inr),
                    "fy_reference": "submission_deadline"
                },
                source=find_quote("turnover_requirement", f"Average turnover of last {n_years} years >= Rs. {turnover_inr}")
            ))

        # 3. UDIN Mandatory Rule
        if eligibility.get("udin_mandatory", True):
            rules.append(Rule(
                rule_id="R-UDIN",
                type=RuleType.IDENTIFIER_PRESENT,
                mandatory=True,
                params={
                    "document_type": DocumentType.CA_TURNOVER_CERTIFICATE.value,
                    "field": "udin"
                },
                source=find_quote("udin_requirement", "CA certificate must carry a valid UDIN.")
            ))

        # 4. NIC Category Rule
        nic_prefixes = eligibility.get("required_nic_prefixes", [])
        if nic_prefixes:
            rules.append(Rule(
                rule_id="R-UDYAM-NIC",
                type=RuleType.FIELD_IN_SET,
                mandatory=True,
                params={
                    "document_type": DocumentType.UDYAM_CERTIFICATE.value,
                    "field": "nic_codes",
                    "match": "any_prefix",
                    "values": nic_prefixes
                },
                source=find_quote("udyam_requirement", f"Udyam certificate must cover NIC category {nic_prefixes}.")
            ))

        return rules

    def _save_rule_pack_to_db(self, rule_pack_id: str, rule_pack: RulePack):
        """Saves rule pack to relational database."""
        with sqlite3.connect(self.storage.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO rule_packs (
                    rule_pack_id, tender_id, version, status,
                    content_hash, rules_json, confirmed_by, confirmed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule_pack_id,
                rule_pack.tender_id,
                rule_pack.version,
                rule_pack.status.value,
                rule_pack.content_hash,
                json.dumps([r.model_dump() for r in rule_pack.rules]),
                rule_pack.confirmed_by,
                rule_pack.confirmed_at.isoformat() if rule_pack.confirmed_at else None,
            ))
            conn.commit()

    def confirm_rule_pack(self, rule_pack_id: str, confirmed_by: str = "user_reviewer") -> Dict[str, Any]:
        """Human confirmation step: Freezes the rule pack so it can drive assessments."""
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.storage.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM rule_packs WHERE rule_pack_id = ?", (rule_pack_id,))
            row = cursor.fetchone()
            if not row:
                return {"success": False, "error": f"Rule pack {rule_pack_id} not found"}

            cursor.execute("""
                UPDATE rule_packs 
                SET status = ?, confirmed_by = ?, confirmed_at = ?
                WHERE rule_pack_id = ?
            """, (RuleStatus.FROZEN.value, confirmed_by, now, rule_pack_id))
            conn.commit()

        return {
            "success": True,
            "rule_pack_id": rule_pack_id,
            "status": RuleStatus.FROZEN.value,
            "confirmed_by": confirmed_by,
            "confirmed_at": now
        }
