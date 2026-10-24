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


class TenderSearchAPIView(APIView):
    """
    GET  /api/v1/tenders/search/?q=services+in+bihar
    POST /api/v1/tenders/search/ {"prompt": "services in bihar above 1 cr"}
    Discovery engine supporting natural language and multi-criteria filters.
    """
    def get(self, request, *args, **kwargs):
        from backend.apps.tenders.search import TenderSearchService, TenderSearchFilter

        prompt = request.query_params.get("q") or request.query_params.get("prompt")
        service = TenderSearchService()
        if prompt:
            res = service.search_by_prompt(prompt)
            return Response(res, status=status.HTTP_200_OK)

        min_val = None
        if "min_value" in request.query_params:
            try:
                min_val = float(request.query_params["min_value"])
            except ValueError:
                pass

        max_val = None
        if "max_value" in request.query_params:
            try:
                max_val = float(request.query_params["max_value"])
            except ValueError:
                pass

        tenure = None
        if "tenure" in request.query_params:
            try:
                tenure = int(request.query_params["tenure"])
            except ValueError:
                pass

        filters = TenderSearchFilter(
            query=request.query_params.get("query"),
            state=request.query_params.get("state"),
            category=request.query_params.get("category"),
            min_value_inr=min_val,
            max_value_inr=max_val,
            min_tenure_months=tenure,
            buyer_name=request.query_params.get("buyer"),
        )
        res = service.search(filters)
        return Response(res, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        from backend.apps.tenders.search import TenderSearchService, TenderSearchFilter

        prompt = request.data.get("prompt") or request.data.get("q")
        service = TenderSearchService()
        if prompt:
            res = service.search_by_prompt(prompt)
            return Response(res, status=status.HTTP_200_OK)

        try:
            filters = TenderSearchFilter(**request.data)
            res = service.search(filters)
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TenderSchemaAPIView(APIView):
    """
    GET /api/v1/tenders/schema/
    Returns the formal JSON Schema for Tender Notice Extractions.
    """
    def get(self, request, *args, **kwargs):
        from backend.engine.schema import TenderPDFExtractionResult
        return Response(TenderPDFExtractionResult.get_json_schema(), status=status.HTTP_200_OK)


class TenderDetailAPIView(APIView):
    """
    GET /api/v1/tenders/<identifier>/?mode=skim|detailed
    Two viewing modes:
    - 'skim': Fast high-level overview
    - 'detailed': Complete breakdown including parsed PDF clauses, page citations, and rule pack
    """
    def get(self, request, identifier, *args, **kwargs):
        mode = request.query_params.get("mode", "skim").lower()
        if mode not in ("skim", "detailed"):
            mode = "skim"

        service = TenderService()
        result = service.get_tender(identifier=identifier, mode=mode)
        if not result:
            return Response(
                {"success": False, "error": f"Tender '{identifier}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(result, status=status.HTTP_200_OK)



