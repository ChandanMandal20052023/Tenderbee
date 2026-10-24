"""
URL endpoints for Tender Intake, PDF Parsing, and RulePack Management.
"""
from django.urls import path

from backend.apps.tenders.views import (
    RulePackConfirmAPIView,
    RulePackDetailAPIView,
    TenderDetailAPIView,
    TenderIntakeAPIView,
    TenderPDFUploadAPIView,
    TenderSearchAPIView,
    TenderSchemaAPIView,
)

urlpatterns = [
    path("schema/", TenderSchemaAPIView.as_view(), name="tender-schema"),
    path("search/", TenderSearchAPIView.as_view(), name="tender-search"),
    path("intake/", TenderIntakeAPIView.as_view(), name="tender-intake"),
    path("upload-pdf/", TenderPDFUploadAPIView.as_view(), name="tender-upload-pdf"),
    path("rule-pack/<str:rule_pack_id>/", RulePackDetailAPIView.as_view(), name="rule-pack-detail"),
    path("rule-pack/<str:rule_pack_id>/confirm/", RulePackConfirmAPIView.as_view(), name="rule-pack-confirm"),
    path("<str:identifier>/", TenderDetailAPIView.as_view(), name="tender-detail"),
]


