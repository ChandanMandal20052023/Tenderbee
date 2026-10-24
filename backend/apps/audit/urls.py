"""
URL endpoints for Immutable Audit Trail.
"""
from django.urls import path
from apps.audit.views import AuditLogListAPIView

app_name = "audit"

urlpatterns = [
    path("", AuditLogListAPIView.as_view(), name="audit-list"),
]
