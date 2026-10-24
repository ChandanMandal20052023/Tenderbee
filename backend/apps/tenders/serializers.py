"""
DRF Serializers for Tender Intake, PDF Parsing, and RulePack Confirmation.
"""
from rest_framework import serializers


class TenderIntakeRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(
        required=True,
        max_length=2048,
        help_text="Procurement URL (e.g. Infralens, GeM) or Tender Number (e.g. GEM/2026/B/894210)",
    )
    org_id = serializers.CharField(
        required=False,
        default="org_default",
        max_length=128,
        help_text="Tenant organization ID",
    )
    force_refresh = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Force scrape bypass of existing snapshot cache",
    )


class TenderPDFUploadSerializer(serializers.Serializer):
    pdf_file = serializers.FileField(
        required=True,
        help_text="Tender Notice PDF file",
    )
    org_id = serializers.CharField(
        required=False,
        default="org_default",
        max_length=128,
        help_text="Tenant organization ID",
    )


class RulePackConfirmSerializer(serializers.Serializer):
    confirmed_by = serializers.CharField(
        required=False,
        default="compliance_lead",
        max_length=128,
        help_text="Identifier of the human reviewer approving the rules",
    )
