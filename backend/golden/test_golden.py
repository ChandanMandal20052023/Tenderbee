"""
Golden-set regression test with CI false-pass gate.
CI fails if any seeded blocking defect gets a READY verdict.
"""
import json
from pathlib import Path
import pytest

from backend.engine.checks import ComplianceEngine
from backend.engine.schema import RulePack, EvidenceItem, VerdictStatus, ReadinessState

GOLDEN_RULES = Path(__file__).parent / "cases" / "rules.json"
GOLDEN_EXPECTED = Path(__file__).parent / "cases" / "expected.json"


def load_rule_pack() -> RulePack:
    with open(GOLDEN_RULES, "r", encoding="utf-8") as f:
        return RulePack(**json.load(f))


def load_test_cases() -> list:
    with open(GOLDEN_EXPECTED, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["test_cases"]


def build_evidence(doc_dict: dict) -> dict:
    """Convert raw JSON test case documents into EvidenceItem-compatible dicts."""
    result = {}
    for doc_type, fields in doc_dict.items():
        result[doc_type] = {}
        for field_name, field_data in fields.items():
            result[doc_type][field_name] = EvidenceItem(**field_data)
    return result


# Structural test
def test_golden_rule_pack_structure():
    """Verifies that golden fixture rules.json adheres to RulePack model."""
    assert GOLDEN_RULES.exists()
    pack = load_rule_pack()
    assert pack.tender_id == "tnd_mech_tpa_2026"
    assert pack.status.value == "FROZEN"
    assert len(pack.rules) == 8


def test_expected_file_exists():
    """Verifies expected.json exists and has 30 test cases."""
    assert GOLDEN_EXPECTED.exists()
    cases = load_test_cases()
    assert len(cases) == 30


# Parametrized test for all 30 cases
@pytest.fixture
def engine():
    return ComplianceEngine()

@pytest.fixture
def rule_pack():
    return load_rule_pack()

@pytest.fixture
def test_cases():
    return load_test_cases()


class TestCleanPasses:
    """Clean pass cases must all reach READY."""
    
    def test_clean_cases_all_ready(self, engine, rule_pack, test_cases):
        clean = [c for c in test_cases if c["category"] == "clean"]
        assert len(clean) == 10, "Expected 10 clean cases"
        for case in clean:
            docs = build_evidence(case["bidder_documents"])
            result = engine.evaluate(rule_pack, docs)
            assert result.readiness.value == case["expected"]["readiness"], \
                f"Case {case['id']}: expected {case['expected']['readiness']}, got {result.readiness.value}"


class TestSeededDefects:
    """CRITICAL CI GATE: No seeded defect may reach READY.
    This is a hard gate — the build fails if any defective case passes."""
    
    def test_no_false_passes_on_defects(self, engine, rule_pack, test_cases):
        """Zero false passes on seeded defects."""
        defects = [c for c in test_cases if c["category"] == "defect"]
        assert len(defects) == 10, "Expected 10 defect cases"
        false_passes = []
        for case in defects:
            docs = build_evidence(case["bidder_documents"])
            result = engine.evaluate(rule_pack, docs)
            if result.readiness.value == "READY":
                false_passes.append(case["id"])
        assert len(false_passes) == 0, \
            f"CI GATE FAILURE: {len(false_passes)} false passes on seeded defects: {false_passes}"
    
    def test_defect_blocked_rules_match(self, engine, rule_pack, test_cases):
        """Each defect case must trigger the expected blocked/review rules."""
        defects = [c for c in test_cases if c["category"] == "defect"]
        for case in defects:
            docs = build_evidence(case["bidder_documents"])
            result = engine.evaluate(rule_pack, docs)
            expected_readiness = case["expected"]["readiness"]
            assert result.readiness.value == expected_readiness, \
                f"Case {case['id']}: expected {expected_readiness}, got {result.readiness.value}"


class TestMessyCases:
    """Messy/edge cases: none should reach READY."""
    
    def test_no_false_passes_on_messy(self, engine, rule_pack, test_cases):
        messy = [c for c in test_cases if c["category"] == "messy"]
        assert len(messy) == 10, "Expected 10 messy cases"
        false_passes = []
        for case in messy:
            docs = build_evidence(case["bidder_documents"])
            result = engine.evaluate(rule_pack, docs)
            if result.readiness.value == "READY":
                false_passes.append(case["id"])
        assert len(false_passes) == 0, \
            f"False passes on messy cases: {false_passes}"


class TestCIGate:
    """Combined CI gate: 0 false passes across defects AND messy cases."""
    
    def test_zero_false_passes_total(self, engine, rule_pack, test_cases):
        """HARD CI GATE: zero false passes on any non-clean case."""
        non_clean = [c for c in test_cases if c["category"] != "clean"]
        false_passes = []
        for case in non_clean:
            docs = build_evidence(case["bidder_documents"])
            result = engine.evaluate(rule_pack, docs)
            if result.readiness.value == "READY":
                false_passes.append(case["id"])
        assert len(false_passes) == 0, \
            f"CI GATE FAILURE: {len(false_passes)} false passes: {false_passes}"
