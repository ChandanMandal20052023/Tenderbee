"""
URL endpoints for Bidder Document Upload and Integrity Management.
"""
from django.urls import path
from apps.documents.views import (
    DocumentDetailAPIView,
    DocumentDownloadAPIView,
    DocumentListAPIView,
    DocumentUploadAPIView,
    JobDetailAPIView,
)

app_name = "documents"

urlpatterns = [
    path("", DocumentListAPIView.as_view(), name="document-list"),
    path("upload/", DocumentUploadAPIView.as_view(), name="document-upload"),
    path("jobs/<str:id>/", JobDetailAPIView.as_view(), name="document-job-detail"),
    path("<str:id>/", DocumentDetailAPIView.as_view(), name="document-detail"),
    path("<str:doc_id>/download/", DocumentDownloadAPIView.as_view(), name="document-download"),
]
