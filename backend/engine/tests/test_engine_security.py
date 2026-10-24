import json
from pathlib import Path

import pytest

from backend.engine.checks import ComplianceEngine
from backend.engine.schema import EvidenceItem, RulePack, RuleStatus, RuleType, VerdictStatus


RULES_PATH = Path(__file__).resolve().parents[2] / "golden" / "cases" / "rules.json"


def load_rule_pack() -> RulePack:
    return RulePack(**json.loads(RULES_PATH.read_text(encoding="utf-8")))


def test_engine_refuses_unfrozen_rule_pack():
    pack = load_rule_pack().model_copy(update={"status": RuleStatus.DRAFT})

    with pytest.raises(ValueError, match="frozen"):
        ComplianceEngine().evaluate(pack, {})


def test_empty_allowed_set_needs_review_instead_of_passing():
    pack = load_rule_pack()
    rule = next(rule for rule in pack.rules if rule.type == RuleType.FIELD_IN_SET)
    unsafe_rule = rule.model_copy(update={"value": []})
    pack = pack.model_copy(update={"rules": [unsafe_rule]})
    documents = {
        "udyam_certificate": {
            "entity_type": EvidenceItem(
                value="Railway PSUs",
                page=1,
                quote="Entity Type: Railway PSUs",
                is_grounded=True,
            )
        }
    }

    result = ComplianceEngine().evaluate(pack, documents)

    assert result.verdicts[0].status == VerdictStatus.NEEDS_REVIEW


def test_field_in_set_requires_exact_value_match():
    pack = load_rule_pack()
    rule = next(rule for rule in pack.rules if rule.type == RuleType.FIELD_IN_SET)
    documents = {
        "udyam_certificate": {
            "entity_type": EvidenceItem(
                value="Railway PSUs with forged eligibility",
                page=1,
                quote="Entity Type: Railway PSUs with forged eligibility",
                is_grounded=True,
            )
        }
    }

    result = ComplianceEngine().evaluate(pack.model_copy(update={"rules": [rule]}), documents)

    assert result.verdicts[0].status == VerdictStatus.BLOCKED


def test_document_presence_alone_cannot_pass_review_flagged_upload():
    pack = load_rule_pack()
    rule = next(rule for rule in pack.rules if rule.type == RuleType.DOCUMENT_REQUIRED)
    rule = rule.model_copy(update={"field": None, "value": None})
    pack = pack.model_copy(update={"rules": [rule]})

    result = ComplianceEngine().evaluate(
        pack,
        {"udyam_certificate": {"__metadata__": {"needs_review": True}}},
    )

    assert result.verdicts[0].status == VerdictStatus.NEEDS_REVIEW


def test_non_finite_numeric_evidence_needs_review():
    pack = load_rule_pack()
    documents = {
        "ca_turnover_certificate": {
            "average_turnover_inr": EvidenceItem(
                value=float("nan"),
                page=1,
                quote="Average annual turnover: Rs. 10",
                is_grounded=True,
            )
        }
    }

    result = ComplianceEngine().evaluate(pack, documents)
    turnover = next(item for item in result.verdicts if item.rule_id == "R-TURNOVER-AVG3")

    assert turnover.status == VerdictStatus.NEEDS_REVIEW


def test_non_finite_rule_threshold_is_rejected_before_evaluation():
    pack = load_rule_pack()
    rule = next(rule for rule in pack.rules if rule.type == RuleType.NUMERIC_THRESHOLD)
    unsafe_rule = rule.model_copy(update={"value": float("inf")})
    pack = pack.model_copy(update={"rules": [unsafe_rule]})

    with pytest.raises(ValueError, match="finite non-negative threshold"):
        ComplianceEngine().evaluate(pack, {})
