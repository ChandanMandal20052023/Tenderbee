"""
Unit and integration tests for Verification Assessment Pipeline (Stages 4-7).
"""
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Organization, User, UserRole
from apps.audit.models import AuditEventType, AuditLogEntry
from apps.documents.models import BidderDocument, DocumentTypeEnum
from apps.evidence.models import EvidenceCitation
from apps.rules.models import RulePack, RulePackItem, RulePackStatus
from apps.tenders.models import Tender
from apps.verify.models import AssessmentStatus, VerificationAssessment


class VerificationPipelineTests(APITestCase):
    def setUp(self):
        self.org = Organization.objects.create(name="HCC Infrastructure Ltd")
        self.user = User.objects.create_user(
            email="lead@hccinfra.in",
            username="hcclead",
            password="HCCPassword2026!",
            organization=self.org,
            role=UserRole.ADMIN,
        )
        self.client.force_authenticate(user=self.user)

        self.tender = Tender.objects.create(
            organization=self.org,
            external_id="RAIL/2026/MECH/5501",
            title="Overhauling and Maintenance of Railway Bogies",
        )

        self.rule_pack = RulePack.objects.create(
            organization=self.org,
            tender=self.tender,
            version=1,
            status=RulePackStatus.FROZEN,
            confirmed_by="Auditor General",
            frozen_hash="frozen_hash_abcdef123456",
        )

        # Rule 1: Udyam certificate required
        RulePackItem.objects.create(
            rule_pack=self.rule_pack,
            rule_id="R-DOC-UDYAM",
            rule_type="document_required",
            description="Udyam MSME Registration Certificate is mandatory.",
            document_type=DocumentTypeEnum.UDYAM,
            parameters={},
        )

        # Rule 2: Minimum 3-year turnover
        RulePackItem.objects.create(
            rule_pack=self.rule_pack,
            rule_id="R-TURNOVER-AVG3",
            rule_type="numeric_threshold",
            description="Minimum average annual turnover must be at least Rs. 2 Crore.",
            document_type=DocumentTypeEnum.CA_TURNOVER,
            parameters={"field": "average_turnover_inr", "operator": ">=", "min_avg_turnover": 20000000.0},
        )

    def test_assessment_blocked_when_documents_missing(self):
        """Verifies that missing compliance documents trigger BLOCKED and populate FixList."""
        eval_url = "/api/v1/verify/evaluate/"
        resp = self.client.post(eval_url, {"tender_id": self.tender.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["success"])
        self.assertEqual(resp.data["overall_status"], AssessmentStatus.BLOCKED.value)
        self.assertGreaterEqual(len(resp.data["missing_documents"]), 1)
        self.assertGreaterEqual(len(resp.data["fix_list"]), 1)

    def test_assessment_ready_when_documents_compliant_and_evidence_created(self):
        """Verifies that compliant documents result in READY, generate evidence citations, and log audit."""
        # Upload compliant Udyam document
        BidderDocument.objects.create(
            organization=self.org,
            tender=self.tender,
            file_name="hcc_udyam.pdf",
            file_path="/tmp/hcc_udyam.pdf",
            document_type=DocumentTypeEnum.UDYAM,
            sha256_hash="1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
            extracted_data={
                "udyam_registration_number": {
                    "value": "UDYAM-MH-01-0099887",
                    "quote": "UDYAM-MH-01-0099887",
                    "page": 1,
                },
                "enterprise_type": {
                    "value": "MEDIUM",
                    "quote": "Type of Enterprise: MEDIUM",
                    "page": 1,
                },
            },
        )

        # Upload compliant CA Turnover document (Avg turnover = 5 Crore >= 2 Crore threshold)
        BidderDocument.objects.create(
            organization=self.org,
            tender=self.tender,
            file_name="hcc_ca_turnover.pdf",
            file_path="/tmp/hcc_ca_turnover.pdf",
            document_type=DocumentTypeEnum.CA_TURNOVER,
            sha256_hash="aaaabbbbccccddddeeeeffff1111222233334444555566667777888899990000",
            extracted_data={
                "average_turnover_inr": {
                    "value": 50000000.0,
                    "quote": "Average Turnover: Rs. 5,00,00,000",
                    "page": 1,
                },
                "udin": {
                    "value": "24089123AAAAAA1234",
                    "quote": "UDIN: 24089123AAAAAA1234",
                    "page": 1,
                },
            },
        )

        eval_url = "/api/v1/verify/evaluate/"
        resp = self.client.post(eval_url, {"tender_id": self.tender.id}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["success"])
        self.assertEqual(resp.data["overall_status"], AssessmentStatus.READY.value)
        self.assertEqual(len(resp.data["missing_documents"]), 0)

        # Verify EvidenceCitations were generated for side-by-side viewer
        ev_resp = self.client.get("/api/v1/evidence/")
        self.assertEqual(ev_resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(ev_resp.data), 1)

        # Verify Audit Log entry
        audit_resp = self.client.get("/api/v1/audit/")
        self.assertEqual(audit_resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(audit_resp.data), 1)
