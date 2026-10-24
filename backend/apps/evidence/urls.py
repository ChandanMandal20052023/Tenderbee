"""
URL endpoints for Evidence Citations and Highlight Bounding Boxes.
"""
from django.urls import path
from apps.evidence.views import EvidenceCitationListAPIView

app_name = "evidence"

urlpatterns = [
    path("", EvidenceCitationListAPIView.as_view(), name="evidence-list"),
]
