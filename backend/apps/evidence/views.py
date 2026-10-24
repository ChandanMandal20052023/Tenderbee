"""
API Views for Evidence Citations and Highlight Bounding Boxes.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.utils import get_tenant_org_id
from apps.evidence.models import EvidenceCitation
from apps.evidence.serializers import EvidenceCitationSerializer


class EvidenceCitationListAPIView(APIView):
    """
    GET /api/v1/evidence/
    Retrieves grounded evidence citations (quote, page number, bounding boxes)
    for side-by-side evidence inspection.
    """
    def get(self, request, *args, **kwargs):
        org_id = get_tenant_org_id(request)
        queryset = EvidenceCitation.objects.filter(organization_id=org_id)

        doc_id = request.query_params.get("document_id")
        if doc_id:
            queryset = queryset.filter(document_id=doc_id)

        field_key = request.query_params.get("field_key")
        if field_key:
            queryset = queryset.filter(field_key=field_key)

        serializer = EvidenceCitationSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
