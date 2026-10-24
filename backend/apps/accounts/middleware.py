"""
Tenant Context Middleware for TenderBee.
Extracts organization context from JWT payload, headers, or authenticated user,
attaching `request.org_id` for multi-tenant isolation.
"""
from typing import Optional
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication


class TenantContextMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.jwt_auth = JWTAuthentication()

    def process_request(self, request):
        request.org_id = "org_default"

        # 1. Try to read from authenticated user if already set
        if hasattr(request, "user") and getattr(request.user, "is_authenticated", False):
            if hasattr(request.user, "organization_id") and request.user.organization_id:
                request.org_id = str(request.user.organization_id)
                return

        # 2. Try to inspect Authorization Bearer header for JWT claims
        header = request.headers.get("Authorization")
        if header and header.startswith("Bearer "):
            try:
                raw_token = header.split(" ")[1]
                validated_token = self.jwt_auth.get_validated_token(raw_token)
                token_org = validated_token.get("org_id")
                if token_org:
                    request.org_id = str(token_org)
                    return
            except Exception:
                pass

        # 3. Fallback to explicit X-Organization-ID header (e.g. for API keys or service tokens)
        header_org = request.headers.get("X-Organization-ID")
        if header_org:
            request.org_id = header_org.strip()
