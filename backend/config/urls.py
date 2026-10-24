"""
Root URL Configuration for TenderBee Backend.
Mounts /api/v1/ and core administrative/health endpoints.
"""
from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


def health_check(request):
    """Liveness and health check endpoint."""
    return JsonResponse({
        "status": "healthy",
        "service": "TenderBee Core API",
        "version": "1.0.0",
        "tenant_id": getattr(request, "org_id", "org_default"),
    })


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health_check, name="health-check"),

    # API v1 routes
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/tenders/", include("apps.tenders.urls")),
    path("api/v1/rules/", include("apps.rules.urls")),
    path("api/v1/documents/", include("apps.documents.urls")),
    path("api/v1/verify/", include("apps.verify.urls")),
    path("api/v1/evidence/", include("apps.evidence.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),
    path("api/v1/find/", include("apps.find.urls")),
    path("api/v1/prepare/", include("apps.prepare.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
