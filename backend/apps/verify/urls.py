"""
URL endpoints for Compliance Assessment, Verification, and Verdicts.
"""
from django.urls import path
from apps.verify.views import (
    AssessmentDetailAPIView,
    AssessmentEvaluateAPIView,
    AssessmentListAPIView,
)

app_name = "verify"

urlpatterns = [
    path("evaluate/", AssessmentEvaluateAPIView.as_view(), name="assessment-evaluate"),
    path("assessments/", AssessmentListAPIView.as_view(), name="assessment-list"),
    path("assessments/<str:assessment_id>/", AssessmentDetailAPIView.as_view(), name="assessment-detail"),
]
