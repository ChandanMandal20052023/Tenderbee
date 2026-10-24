"""
API Views for Tender Intake, PDF Parsing, and RulePack Management.
"""
import os
import tempfile
from pathlib import Path
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.apps.tenders.services import TenderService
from backend.apps.tenders.serializers import (
    RulePackConfirmSerializer,
    TenderIntakeRequestSerializer,
    TenderPDFUploadSerializer,
)


class TenderIntakeAPIView(APIView):
    """
    POST /api/tenders/intake/
    Accepts a procurement URL or tender number, scrapes or loads from cache,
    and automatically drafts an executable RulePack.
    """
    def post(self, request, *args, **kwargs):
        serializer = TenderIntakeRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        identifier = serializer.validated_data["identifier"]
        org_id = serializer.validated_data["org_id"]
        force_refresh = serializer.validated_data["force_refresh"]

        service = TenderService()
        result = service.intake_tender(
            identifier=identifier,
            org_id=org_id,
            force_refresh=force_refresh,
        )

        if not result.get("success"):
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(result, status=status.HTTP_200_OK)


class TenderPDFUploadAPIView(APIView):
    """
    POST /api/tenders/upload-pdf/
    Uploads an Indian procurement tender PDF, extracts clauses and parameters,
    and returns a structured JSON schema along with a draft RulePack.
    """
    def post(self, request, *args, **kwargs):
        serializer = TenderPDFUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        pdf_file = serializer.validated_data["pdf_file"]
        org_id = serializer.validated_data["org_id"]

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            for chunk in pdf_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            service = TenderService()
            result = service.intake_tender_pdf(pdf_path=tmp_path, org_id=org_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"success": False, "error": f"PDF parsing failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class RulePackConfirmAPIView(APIView):
    """
    POST /api/tenders/rule-pack/<rule_pack_id>/confirm/
    Locks and freezes a draft RulePack with cryptographic SHA-256 integrity hash.
    """
    def post(self, request, rule_pack_id, *args, **kwargs):
        serializer = RulePackConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        confirmed_by = serializer.validated_data["confirmed_by"]
        service = TenderService()
        result = service.confirm_rule_pack(rule_pack_id=rule_pack_id, confirmed_by=confirmed_by)

        if not result.get("success"):
            return Response(result, status=status.HTTP_404_NOT_FOUND)

        return Response(result, status=status.HTTP_200_OK)


class RulePackDetailAPIView(APIView):
    """
    GET /api/tenders/rule-pack/<rule_pack_id>/
    Retrieves a RulePack by ID.
    """
    def get(self, request, rule_pack_id, *args, **kwargs):
        service = TenderService()
        rule_pack = service.get_rule_pack(rule_pack_id=rule_pack_id)
        if not rule_pack:
            return Response(
                {"success": False, "error": f"RulePack '{rule_pack_id}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(rule_pack.model_dump(), status=status.HTTP_200_OK)
