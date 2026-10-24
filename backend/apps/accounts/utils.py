"""
Tenant isolation utilities.
"""
def get_tenant_org_id(request) -> str:
    """
    Safely resolves the current tenant organization ID from authenticated user,
    JWT token claims, or request middleware attributes.
    """
    if getattr(request, "user", None) and getattr(request.user, "is_authenticated", False):
        if getattr(request.user, "organization_id", None):
            return str(request.user.organization_id)
    return getattr(request, "org_id", "org_default")
