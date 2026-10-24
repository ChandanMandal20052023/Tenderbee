"""
Rule Pack Lifecycle Service for TenderBee.
Manages drafting, human review, updating individual rules, and cryptographic freezing.
"""
from typing import Any, Dict, List, Optional

from backend.apps.tenders.services import TenderService
from backend.engine.schema import Rule, RulePack, RuleStatus


class RuleService:
    def __init__(self, tender_service: Optional[TenderService] = None):
        self.tender_service = tender_service or TenderService()

    def get_rule_pack(self, rule_pack_id: str) -> Optional[RulePack]:
        """Retrieves RulePack by ID."""
        return self.tender_service.get_rule_pack(rule_pack_id)

    def freeze_rule_pack(self, rule_pack_id: str, confirmed_by: str = "compliance_lead") -> Dict[str, Any]:
        """Cryptographically freezes a rule pack, making it immutable for compliance audits."""
        return self.tender_service.confirm_rule_pack(rule_pack_id=rule_pack_id, confirmed_by=confirmed_by)
