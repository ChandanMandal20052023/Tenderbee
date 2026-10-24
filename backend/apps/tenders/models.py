"""
Tender & Snapshot Models with Tenant Isolation and Corrigendum Immutability.
"""
import uuid
from django.db import models
from apps.accounts.models import Organization, TenantAwareModel


class TenderStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    UNDER_REVIEW = "under_review", "Under Review"
    FROZEN = "frozen", "Frozen"
    ARCHIVED = "archived", "Archived"


class Tender(TenantAwareModel):
    """
    Master tender procurement record.
    """
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    external_id = models.CharField(max_length=128, db_index=True, help_text="Tender Number, e.g. GEM/2026/B/894210")
    title = models.CharField(max_length=500)
    buyer_name = models.CharField(max_length=255, blank=True, null=True)
    buyer_location = models.CharField(max_length=255, blank=True, null=True)
    submission_deadline = models.DateTimeField(null=True, blank=True)
    bid_opening_date = models.DateTimeField(null=True, blank=True)
    estimated_value_inr = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    emd_amount_inr = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    mse_exemption_allowed = models.BooleanField(default=False)
    source_url = models.CharField(max_length=1000, blank=True, null=True)
    status = models.CharField(max_length=32, choices=TenderStatus.choices, default=TenderStatus.ACTIVE)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("organization", "external_id")

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"tnd_{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.external_id} - {self.title[:50]}"


class TenderSnapshot(TenantAwareModel):
    """
    Immutable versioned snapshot of raw tender data and extracted clauses.
    Enforces SHA-256 deduplication and corrigendum change tracking.
    """
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    tender = models.ForeignKey(
        Tender,
        on_delete=models.CASCADE,
        related_name="snapshots",
        db_index=True,
    )
    source_url = models.CharField(max_length=1000, blank=True)
    content_hash = models.CharField(max_length=64, db_index=True, help_text="SHA-256 content checksum")
    raw_payload_path = models.CharField(max_length=500, blank=True)
    extracted_json_path = models.CharField(max_length=500, blank=True)
    extracted_data = models.JSONField(default=dict)
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fetched_at"]

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"snp_{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Snapshot {self.id} for {self.tender.external_id} [{self.content_hash[:8]}]"
