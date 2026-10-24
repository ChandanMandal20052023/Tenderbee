"""
Evidence Citation Models linking facts to document pages and verbatim text quotes.
"""
import uuid
from django.db import models
from apps.accounts.models import TenantAwareModel
from apps.documents.models import BidderDocument


class EvidenceCitation(TenantAwareModel):
    """
    Side-by-side evidence link connecting extracted facts directly to source page and bounding boxes.
    """
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    document = models.ForeignKey(
        BidderDocument,
        on_delete=models.CASCADE,
        related_name="citations",
        db_index=True,
    )
    field_key = models.CharField(max_length=128, db_index=True)
    page_number = models.PositiveIntegerField(default=1)
    quote = models.TextField()
    bounding_box = models.JSONField(default=dict, help_text="Coordinates {x1, y1, x2, y2} for PDF highlight")
    confidence = models.FloatField(default=1.0)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"ev_{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Citation for {self.field_key} on page {self.page_number} ({self.id})"
