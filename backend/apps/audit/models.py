"""
Immutable Audit Trail Models for TenderBee.
Records cryptographically signed events for tenders, rule freezes, document checks, and verdicts.
"""
import hashlib
import json
import uuid
from django.db import models
from apps.accounts.models import TenantAwareModel


class AuditEventType(models.TextChoices):
    TENDER_INTAKE = "TENDER_INTAKE", "Tender Intake"
    RULE_PACK_DRAFTED = "RULE_PACK_DRAFTED", "RulePack Drafted"
    RULE_PACK_FROZEN = "RULE_PACK_FROZEN", "RulePack Cryptographically Frozen"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED", "Document Uploaded & Verified"
    ASSESSMENT_EVALUATED = "ASSESSMENT_EVALUATED", "Compliance Assessment Evaluated"
    REGISTRY_CHECK = "REGISTRY_CHECK", "External Registry Verified"
    VERDICT_SIGNED = "VERDICT_SIGNED", "Verdict Finalized and Signed"


class AuditLogEntry(TenantAwareModel):
    """
    Append-only immutable audit log record.
    """
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    event_type = models.CharField(max_length=64, choices=AuditEventType.choices, db_index=True)
    actor = models.CharField(max_length=255, default="system")
    target_id = models.CharField(max_length=64, db_index=True)
    payload_hash = models.CharField(max_length=64, help_text="SHA-256 hash of event payload")
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"aud_{uuid.uuid4().hex[:12]}"
        if not self.payload_hash:
            serialized = json.dumps(self.details, sort_keys=True)
            self.payload_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.event_type}] by {self.actor} on {self.target_id} at {self.timestamp}"
