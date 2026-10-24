"""
Serializers for Evidence Citations and Highlight Bounding Boxes.
"""
from rest_framework import serializers
from apps.evidence.models import EvidenceCitation


class EvidenceCitationSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source="document.file_name", read_only=True)
    document_type = serializers.CharField(source="document.document_type", read_only=True)

    class Meta:
        model = EvidenceCitation
        fields = (
            "id",
            "document",
            "document_name",
            "document_type",
            "field_key",
            "page_number",
            "quote",
            "bounding_box",
            "confidence",
            "created_at",
        )
        read_only_fields = fields
