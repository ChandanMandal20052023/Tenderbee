"""
RulePack Models for deterministic compliance criteria with cryptographic freezing.
"""
import hashlib
import json
import uuid
from django.db import models
from apps.accounts.models import TenantAwareModel
from apps.tenders.models import Tender


class RulePackStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    FROZEN = "FROZEN", "Frozen"
    ARCHIVED = "ARCHIVED", "Archived"


class RulePack(TenantAwareModel):
    """
    Container for frozen or draft compliance criteria governing a specific tender.
    """
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    tender = models.ForeignKey(
        Tender,
        on_delete=models.CASCADE,
        related_name="rule_packs",
        db_index=True,
    )
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=32,
        choices=RulePackStatus.choices,
        default=RulePackStatus.DRAFT,
    )
    content_hash = models.CharField(max_length=64, blank=True, help_text="SHA-256 of active rules payload")
    rules_data = models.JSONField(default=list)
    reference_dates = models.JSONField(default=dict)
    confirmed_by = models.CharField(max_length=255, blank=True, null=True)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    frozen_hash = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ["-version"]
        unique_together = ("tender", "version")

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"rp_{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)

    def compute_hash(self) -> str:
        serialized = json.dumps(
            {"rules": self.rules_data, "reference_dates": self.reference_dates},
            sort_keys=True,
        )
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def freeze(self, confirmed_by_name: str):
        """Freezes the RulePack, rendering it immutable for compliance audits."""
        from django.utils import timezone
        self.status = RulePackStatus.FROZEN
        self.confirmed_by = confirmed_by_name
        self.confirmed_at = timezone.now()
        self.content_hash = self.compute_hash()
        self.frozen_hash = self.content_hash
        self.save()

    def __str__(self):
        return f"RulePack {self.id} (Tender: {self.tender.external_id}, v{self.version}) [{self.status}]"


class RulePackItem(models.Model):
    """
    Individual rule inside a RulePack (e.g. R-TURNOVER-AVG3, R-DOC-UDYAM).
    """
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    rule_pack = models.ForeignKey(
        RulePack,
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
    )
    rule_id = models.CharField(max_length=64, db_index=True)
    rule_type = models.CharField(max_length=64)
    description = models.TextField()
    document_type = models.CharField(max_length=64)
    parameters = models.JSONField(default=dict)
    quote = models.TextField(blank=True)
    page = models.IntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)
    is_dismissed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"r_{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.rule_id}: {self.description[:40]}"
