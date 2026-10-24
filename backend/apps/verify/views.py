"""
API Views for Verification Assessments, Deterministic Rules Execution, and Verdict Overrides.
Enforces:
- Members can run and view assessments for their own organization.
- Only Reviewers or Owners can override verdicts with a mandatory reason.
- Overrides never delete or overwrite the original verdict.
- Cross-tenant access strictly returns 404.
"""
from django.http import Http404
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsMember, IsReviewerOrOwner, TenantIsolationMixin
from apps.audit.models import AuditEventType
from apps.audit.services import record_audit_event
from apps.verify.models import VerificationAssessment
from apps.verify.serializers import (
    AssessmentRequestSerializer,
    VerdictOverrideSerializer,
    VerificationAssessmentSerializer,
)
from apps.verify.services import VerificationService


class AssessmentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


class AssessmentEvaluateAPIView(APIView):
    """
    POST /api/v1/verify/evaluate/
    Executes the 7-stage deterministic verification pipeline for the current tenant.
    """
    permission_classes = [IsMember]

    def post(self, request, *args, **kwargs):
        serializer = AssessmentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tender_id = serializer.validated_data["tender_id"]
        rule_pack_id = serializer.validated_data.get("rule_pack_id")
        user = request.user
        org = user.organization

        service = VerificationService()
        result = service.run_assessment(
            tender_id=tender_id,
            organization_id=str(org.id),
            rule_pack_id=rule_pack_id if rule_pack_id else None,
            actor=user.email,
        )

        if not result.get("success"):
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        return Response(result, status=status.HTTP_200_OK)


class AssessmentListAPIView(TenantIsolationMixin, generics.ListAPIView):
    """
    GET /api/v1/verify/assessments/
    Paginated list of assessments for the authenticated tenant.
    """
    serializer_class = VerificationAssessmentSerializer
    permission_classes = [IsMember]
    pagination_class = AssessmentPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        tender_id = self.request.query_params.get("tender_id")
        if tender_id:
            queryset = queryset.filter(tender_id=tender_id)
        return queryset


class AssessmentDetailAPIView(TenantIsolationMixin, generics.RetrieveAPIView):
    """
    GET /api/v1/verify/assessments/<id>/
    Retrieves full audit report for an assessment with cross-tenant 404 isolation.
    """
    serializer_class = VerificationAssessmentSerializer
    permission_classes = [IsMember]
    queryset = VerificationAssessment.objects.all()
    lookup_field = "id"


class AssessmentVerdictOverrideAPIView(APIView):
    """
    POST /api/v1/verify/assessments/<assessment_id>/override/
    Allows Reviewers and Owners to review and override an automated rule verdict
    with a mandatory reason. Never deletes or mutates the original verdict data.
    """
    permission_classes = [IsReviewerOrOwner]

    def post(self, request, assessment_id, *args, **kwargs):
        user = request.user
        org = user.organization

        try:
            assessment = VerificationAssessment.objects.get(id=assessment_id, organization=org)
        except VerificationAssessment.DoesNotExist:
            raise Http404("Assessment not found.")

        serializer = VerdictOverrideSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        rule_id = serializer.validated_data["rule_id"]
        new_verdict = serializer.validated_data["new_verdict"]
        reason = serializer.validated_data["reason"]

        # Find original verdict
        orig_verdict = "UNKNOWN"
        for v in assessment.verdicts_data:
            if isinstance(v, dict) and (v.get("rule_id") == rule_id or v.get("id") == rule_id):
                orig_verdict = v.get("verdict", "UNKNOWN")
                break

        override_entry = {
            "rule_id": rule_id,
            "original_verdict": orig_verdict,
            "new_verdict": new_verdict,
            "reason": reason,
            "overridden_by": user.email,
            "timestamp": timezone.now().isoformat(),
        }

        # Append override without modifying original verdicts_data
        overrides = list(assessment.verdict_overrides)
        overrides.append(override_entry)
        assessment.verdict_overrides = overrides
        assessment.save(update_fields=["verdict_overrides"])

        # Write immutable audit log
        record_audit_event(
            organization=org,
            actor=user.email,
            event_type=AuditEventType.VERDICT_OVERRIDE,
            target_id=f"{assessment.id}:{rule_id}",
            details=override_entry,
        )

        return Response(
            {
                "success": True,
                "message": f"Verdict for rule {rule_id} overridden to {new_verdict}.",
                "override": override_entry,
                "assessment": VerificationAssessmentSerializer(assessment).data,
            },
            status=status.HTTP_200_OK,
        )
