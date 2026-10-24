"""
Audit recording helper service for TenderBee.
Provides centralized logging of security, domain, and data lifecycle events.
"""
from typing import Any, Dict, Optional
from apps.accounts.models import Organization
from apps.audit.models import AuditEventType, AuditLogEntry


def record_audit_event(
    organization: Organization,
    actor: str,
    event_type: str,
    target_id: str,
    details: Optional[Dict[str, Any]] = None,
) -> AuditLogEntry:
    """
    Creates an immutable audit log entry scoped to the given organization.
    """
    if not organization:
        raise ValueError("Audit event requires a valid Organization tenant.")
        
    return AuditLogEntry.objects.create(
        organization=organization,
        actor=actor or "system",
        event_type=event_type,
        target_id=str(target_id),
        details=details or {},
    )


class AuditTrailService:
    """Service wrapper for logging and querying audit events."""
    @staticmethod
    def record_event(organization, actor, event_type, target_id, details=None):
        return record_audit_event(organization, actor, event_type, target_id, details)

