"""
DRF Serializers for RulePacks and RuleItems.
"""
from rest_framework import serializers
from apps.rules.models import RulePack, RulePackItem, RulePackStatus


class RulePackItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = RulePackItem
        fields = (
            "id",
            "rule_id",
            "rule_type",
            "description",
            "document_type",
            "parameters",
            "quote",
            "page",
            "is_mandatory",
            "is_dismissed",
        )


class RulePackItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RulePackItem
        fields = ("is_dismissed", "parameters", "description")


class RulePackSerializer(serializers.ModelSerializer):
    items = RulePackItemSerializer(many=True, read_only=True)
    tender_external_id = serializers.CharField(source="tender.external_id", read_only=True)

    class Meta:
        model = RulePack
        fields = (
            "id",
            "tender",
            "tender_external_id",
            "version",
            "status",
            "content_hash",
            "frozen_hash",
            "confirmed_by",
            "confirmed_at",
            "rules_data",
            "reference_dates",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "version", "content_hash", "frozen_hash", "confirmed_at", "created_at", "updated_at")


class RulePackFreezeSerializer(serializers.Serializer):
    confirmed_by = serializers.CharField(
        required=False,
        default="compliance_lead",
        max_length=128,
        help_text="Name or role of the compliance officer freezing the rules",
    )
