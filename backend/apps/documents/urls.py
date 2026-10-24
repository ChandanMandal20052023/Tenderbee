"""
URL endpoints for Bidder Document Upload and Integrity Management.
"""
from django.urls import path
from apps.documents.views import (
    DocumentDetailAPIView,
    DocumentListAPIView,
    DocumentUploadAPIView,
)

app_name = "documents"

urlpatterns = [
    path("", DocumentListAPIView.as_view(), name="document-list"),
    path("upload/", DocumentUploadAPIView.as_view(), name="document-upload"),
    path("<str:doc_id>/", DocumentDetailAPIView.as_view(), name="document-detail"),
]
