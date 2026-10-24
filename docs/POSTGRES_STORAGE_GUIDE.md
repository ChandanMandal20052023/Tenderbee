# TenderBee PostgreSQL Storage & Backend Hand-Off Guide

> **Target Audience:** Backend Engineer / Database Developer  
> **Purpose:** Hand-off guide for implementing production PostgreSQL + S3 tiered storage for TenderBee.

---

## 1. Architecture Overview

TenderBee decouples tender storage into **3 tables** to support multi-tenant isolation, immutable audit trails, and government tender amendments (corrigendums):

```
+------------------------------------------------------------------------+
| TIER 1: PostgreSQL Database                                            |
|                                                                        |
| 1. tenders           -> Master identity & metadata (title, dates, val) |
| 2. tender_snapshots  -> Immutable fetch logs & SHA-256 content hashes  |
| 3. rule_packs        -> Versioned compliance rule requirements (JSONB) |
+------------------------------------------------------------------------+
                               |
                               | Points to
                               v
+------------------------------------------------------------------------+
| TIER 2: Object Storage (AWS S3 / MinIO / Local Disk)                  |
|                                                                        |
| • snapshots/{sha256}_raw.txt       -> Raw scraped text / markdown      |
| • snapshots/{sha256}_extracted.json-> Fully structured JSON extraction |
+------------------------------------------------------------------------+
```

---

## 2. Core Design Rules (Non-Negotiable)

1. **Multi-Tenant Isolation (`organization_id`):**  
   Every table must carry `organization_id`. All queries must filter by `organization_id` to ensure Bidder A never accesses Bidder B's tender drafts.
2. **Immutable Snapshots (Never `UPDATE` a Snapshot):**  
   Government portals frequently issue amendments (corrigendums). Each fetch hashes the scraped content using **SHA-256**. If the hash changes, a **new `tender_snapshots` row** is created. Never overwrite historical snapshots.
3. **Rule Pack Freezing:**  
   Rule packs start in `DRAFT` status. A compliance assessment can **only** be executed against a rule pack whose status is **`FROZEN`**. Freezing writes an append-only audit record (`confirmed_by`, `confirmed_at`).

---

## 3. PostgreSQL Schema (DDL)

Run these SQL statements directly in your PostgreSQL database:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Master Tenders Table
CREATE TABLE IF NOT EXISTS tenders (
    tender_id VARCHAR(64) PRIMARY KEY,
    organization_id VARCHAR(64) NOT NULL,
    external_id VARCHAR(128) NOT NULL, -- e.g. "GEM/2026/B/894210"
    title TEXT NOT NULL,
    buyer_name VARCHAR(255),
    buyer_location VARCHAR(255),
    submission_deadline TIMESTAMPTZ NOT NULL,
    bid_opening TIMESTAMPTZ,
    estimated_value_inr NUMERIC(15, 2),
    emd_amount_inr NUMERIC(15, 2),
    mse_exemption_allowed BOOLEAN DEFAULT TRUE,
    source_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tenders_org_external ON tenders(organization_id, external_id);
CREATE INDEX idx_tenders_deadline ON tenders(submission_deadline);

-- 2. Immutable Tender Snapshots Table
CREATE TABLE IF NOT EXISTS tender_snapshots (
    snapshot_id VARCHAR(64) PRIMARY KEY,
    tender_id VARCHAR(64) NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    organization_id VARCHAR(64) NOT NULL,
    source_url TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of scraped payload
    raw_payload_url TEXT NOT NULL,      -- S3 URL or path to raw text/markdown
    extracted_json_url TEXT NOT NULL,   -- S3 URL or path to structured JSON
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_snapshots_org_url ON tender_snapshots(organization_id, source_url);
CREATE INDEX idx_snapshots_hash ON tender_snapshots(content_hash);

-- 3. Versioned Rule Packs Table
CREATE TABLE IF NOT EXISTS rule_packs (
    rule_pack_id VARCHAR(64) PRIMARY KEY,
    tender_id VARCHAR(64) NOT NULL REFERENCES tenders(tender_id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(32) NOT NULL DEFAULT 'DRAFT', -- 'DRAFT' | 'IN_REVIEW' | 'CONFIRMED' | 'FROZEN'
    content_hash VARCHAR(64) NOT NULL,
    rules_json JSONB NOT NULL,                   -- List of Rule objects matching Pydantic schema
    confirmed_by VARCHAR(64),
    confirmed_at TIMESTAMPTZ
);

CREATE INDEX idx_rulepacks_tender_version ON rule_packs(tender_id, version);
CREATE INDEX idx_rulepacks_rules_gin ON rule_packs USING GIN (rules_json);
```

---

## 4. Django ORM Implementation (`apps/tenders/models.py`)

If you are using Django / Django REST Framework, use these models:

```python
from django.db import models


class Tender(models.Model):
    tender_id = models.CharField(max_length=64, primary_key=True)
    organization_id = models.CharField(max_length=64, db_index=True)
    external_id = models.CharField(max_length=128, db_index=True)
    title = models.TextField()
    buyer_name = models.CharField(max_length=255, null=True, blank=True)
    buyer_location = models.CharField(max_length=255, null=True, blank=True)
    submission_deadline = models.DateTimeField(db_index=True)
    bid_opening = models.DateTimeField(null=True, blank=True)
    estimated_value_inr = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    emd_amount_inr = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    mse_exemption_allowed = models.BooleanField(default=True)
    source_url = models.URLField(max_length=1024, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["organization_id", "external_id"]),
        ]


class TenderSnapshot(models.Model):
    snapshot_id = models.CharField(max_length=64, primary_key=True)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="snapshots")
    organization_id = models.CharField(max_length=64, db_index=True)
    source_url = models.URLField(max_length=1024)
    content_hash = models.CharField(max_length=64, db_index=True)
    raw_payload_url = models.TextField()
    extracted_json_url = models.TextField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fetched_at"]


class RulePack(models.Model):
    rule_pack_id = models.CharField(max_length=64, primary_key=True)
    tender = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="rule_packs")
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=32,
        choices=[("DRAFT", "Draft"), ("CONFIRMED", "Confirmed"), ("FROZEN", "Frozen")],
        default="DRAFT"
    )
    content_hash = models.CharField(max_length=64)
    rules_json = models.JSONField()  # Stores Pydantic Rule dicts
    confirmed_by = models.CharField(max_length=64, null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
```

---

## 5. How to Expose the REST API Endpoints

In your Django views or FastAPI routes, connect directly to `TenderService`:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tenderbee.apps.tenders.service import TenderService

service = TenderService()

class TenderIngestView(APIView):
    """
    POST /api/v1/tenders/ingest/
    Body: {"identifier": "GEM/2026/B/894210" or "https://...", "organization_id": "org_1"}
    """
    def post(self, request):
        identifier = request.data.get("identifier")
        org_id = request.data.get("organization_id", "default_org")
        
        result = service.intake_tender(identifier=identifier, org_id=org_id)
        if not result.get("success"):
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result, status=status.HTTP_200_OK)


class RulePackConfirmView(APIView):
    """
    POST /api/v1/rule-packs/{id}/confirm/
    Body: {"confirmed_by": "user_123"}
    """
    def post(self, request, rule_pack_id):
        user_id = request.data.get("confirmed_by", "anonymous")
        freeze_result = service.confirm_rule_pack(rule_pack_id, confirmed_by=user_id)
        return Response(freeze_result, status=status.HTTP_200_OK)
```

---

## 6. S3 Object Storage Settings (Production)

In `.env`, configure:
```ini
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=tenderbee-snapshots
AWS_S3_REGION_NAME=ap-south-1
```
When `STORAGE_BACKEND=s3` is enabled, `save_tender_and_snapshot` uploads `{hash}_raw.txt` and `{hash}_extracted.json` to S3 and stores the S3 URL in PostgreSQL!
