"""
Accounts & Organization models with Multi-Tenant isolation.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class Organization(models.Model):
    """
    Tenant entity isolating all tenders, documents, rulepacks, and verdicts.
    """
    id = models.CharField(primary_key=True, max_length=64, editable=False)
    name = models.CharField(max_length=255)
    gstin = models.CharField(max_length=15, blank=True, null=True)
    udyam_number = models.CharField(max_length=30, blank=True, null=True)
    pan = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = f"org_{uuid.uuid4().hex[:12]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.id})"


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    BID_MANAGER = "bid_manager", "Bid Manager"
    VIEWER = "viewer", "Viewer"


class User(AbstractUser):
    """
    Custom user model authenticated via email and linked to an Organization tenant.
    """
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="members",
        null=True,
        blank=True,
    )
    role = models.CharField(
        max_length=32,
        choices=UserRole.choices,
        default=UserRole.BID_MANAGER,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def organization_id(self):
        return self.organization.id if self.organization else None

    def __str__(self):
        return f"{self.email} [{self.role}]"


class TenantAwareModel(models.Model):
    """
    Abstract base model enforcing organization tenant isolation and audit timestamps.
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
