"""
Serializers for Immutable Audit Trail.
"""
from rest_framework import serializers
from apps.audit.models import AuditLogEntry


class AuditLogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLogEntry
        fields = (
            "id",
            "event_type",
            "actor",
            "target_id",
            "payload_hash",
            "details",
            "timestamp",
        )
        read_only_fields = fields
