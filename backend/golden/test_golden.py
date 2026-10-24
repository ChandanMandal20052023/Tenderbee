"""
Golden fixture regression test verifying standard compliance rules evaluation.
"""
import json
from pathlib import Path
import pytest

from backend.engine.checks import ComplianceEngine
from backend.engine.schema import RulePack

GOLDEN_RULES = Path(__file__).parent / "cases" / "rules.json"


def test_golden_rule_pack_structure():
    """Verifies that golden fixture rules.json adheres to RulePack model."""
    assert GOLDEN_RULES.exists(), f"Missing golden rules file: {GOLDEN_RULES}"
    with open(GOLDEN_RULES, "r", encoding="utf-8") as f:
        data = json.load(f)
    pack = RulePack(**data)
    assert pack.tender_id == "tnd_mech_tpa_2026"
    assert pack.status.value == "FROZEN"
    assert len(pack.rules) == 8
