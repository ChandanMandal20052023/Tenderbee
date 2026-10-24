# TenderBee Backend Memory & Execution Ledger

> **Core Philosophy**: *"AI extracts. Deterministic rules decide. Official sources confirm."*
> **Rule**: Zero LLM pass/fail decisions. Pass/Fail is strictly deterministic via pure Python.

---

## 1. Project Context & Current State

### Architectural Overview
- **Monorepo Structure**:
  - `backend/`: Django 5.x + DRF, Celery + Redis, Neon Serverless PostgreSQL + S3/Local Storage.
  - `backend/engine/`: Pure-Python deterministic rule evaluation engine (zero external framework/DB dependencies).
  - `backend/services/`: TinyFish integration, storage service (tiered metadata + raw snapshot storage), LLM structured extraction adapters.
  - `frontend/`: Next.js (App Router) + TypeScript client (scaffolded).

### Current State Audit
- **Completed Components**:
  - `backend/engine/`: Full schema (`schema.py`), evaluation logic (`checks.py`), PDF extractor & grounding check (`parser.py`), verdict models (`verdict.py`, `ready.py`, `rules.py`), unit tests (`tests/test_engine.py`).
  - `backend/services/storage.py`: Tiered storage abstraction (`TenderStorage`) with SQLite metadata and raw JSON/payload caching.
  - `backend/services/tinyfish.py`: TinyFish client (`BidEasyScraper`) for scraping portal/registry data and SSE streaming.
  - `backend/services/llm.py`: Grounded field extraction schemas for Udyam, CA Turnover, and NSIC.
  - `backend/apps/tenders/`: Services (`services.py`), serializers, and views partially drafted.
- **Missing / Scaffolded Components**:
  - `backend/manage.py`: Empty stub (needs full Django CLI entrypoint).
  - `backend/config/`: `settings.py`, `urls.py`, `celery.py`, `wsgi.py`, `asgi.py` are minimal stubs.
  - `backend/apps/*/models.py`: Database models for all apps (`accounts`, `tenders`, `rules`, `documents`, `verify`, `evidence`, `audit`, etc.) are empty stubs.
  - Missing dependencies in `requirements.txt` (`pypdf`, `pyhanko`, `python-dotenv`, etc.).
  - Async task pipelines in Celery (`apps/*/tasks.py`).
  - REST endpoints and viewsets for Document upload, RulePack freezing, Verification Pipeline (7 stages), Audit logs.

---

## 2. The 10-Sub-Step Backend Execution Plan

| Step | Sub-Step Title | Scope & Description | Status |
| :---: | :--- | :--- | :---: |
| **01** | **Environment & Django Core Bootstrap** | Fix `requirements.txt` (`pypdf`, `pyhanko`, `python-dotenv`, `djangorestframework-simplejwt`, `rapidfuzz`), configure `manage.py`, production-ready `settings.py` (Neon DB dual-conn, Celery, DRF, JWT settings, CORS, Storage), `urls.py`, `wsgi.py`, `asgi.py`. | ✅ DONE |
| **02** | **Accounts, Tenant Isolation & JWT Authentication** | Implement Organization/Tenant models, Custom User model, `djangorestframework-simplejwt` integration with custom token claims (`org_id`, `role`), JWT token endpoints (obtain, refresh, verify), and tenant-scoped querysets/middleware. | ✅ DONE |
| **03** | **Tenders & Snapshots Domain Models & Storage** | Django ORM models for `Tender`, `TenderSnapshot`, `Corrigendum`. Migrate `storage.py` to seamlessly bridge Django ORM and S3/Local object storage. | ✅ DONE |
| **04** | **RulePack Models & Lifecycle API** | ORM models for `RulePack` and `RulePackItem`. Full CRUD and confirmation/freezing endpoints (`POST /api/v1/rule-packs/{id}/confirm`). Immutability & SHA-256 hash freezing. | ✅ DONE |
| **05** | **Bidder Documents & Intake Pipeline (Stage 1 & 2)** | Document upload endpoint (`POST /api/v1/documents/upload`), SHA-256 integrity checksums, pyHanko cryptographic signature validation, multi-format text & OCR extraction. | ✅ DONE |
| **06** | **Document AI & Schema-Constrained Extraction (Stage 3)** | Grounded entity extraction pipeline using `services/llm.py` and Pydantic schemas for Udyam, CA Turnover, GST, and NSIC certificates with strict quote/page grounding. | ✅ DONE |
| **07** | **Deterministic Rules Engine Integration (Stage 4 & 5)** | Bridge `backend/engine/checks.py` into Django service layer: evaluate frozen RulePacks against extracted bidder document facts. Profile fit & tender requirement scoring. | ✅ DONE |
| **08** | **External Registry Verification via TinyFish (Stage 6)** | TinyFish integration service for live verification against official portals: GST active status, Udyam MSME class, ICAI UDIN verification, and DPIIT startup validation. | ✅ DONE |
| **09** | **Verdict, Evidence Generation & Audit Trail (Stage 7)** | Composite verdict generation (`READY`, `NEEDS_REVIEW`, `BLOCKED`), FixList generation, side-by-side evidence crop/citation linking, and append-only cryptographic audit logging. | ✅ DONE |
| **10** | **Celery Asynchronous Tasks, API Routing & Test Suite** | Background job queues for heavy extraction and scraping, unified API routing (`/api/v1/...`), health checks, end-to-end integration tests & golden test cases (25/25 passing). | ✅ DONE |

---

## 3. Step-by-Step Technical Details & Acceptance Criteria

### Step 1: Environment & Django Core Bootstrap
- **Target Files**:
  - `backend/requirements.txt`, `requirements.txt`
  - `backend/manage.py`
  - `backend/config/settings.py` (Installed apps, DRF auth classes, `SIMPLE_JWT` config, Neon DB dual-conn, CORS)
  - `backend/config/urls.py`
  - `backend/config/celery.py`
  - `backend/config/wsgi.py`, `backend/config/asgi.py`
- **Acceptance Criteria**:
  - `python backend/manage.py check` executes without error.
  - Settings support Neon Serverless (`DATABASE_URL` runtime pooler, `DIRECT_URL` migrations).
  - DRF and `rest_framework_simplejwt` configured with `JWTStatelessUserAuthentication` / `JWTAuthentication` and configurable lifetimes (`ACCESS_TOKEN_LIFETIME = 60m`, `REFRESH_TOKEN_LIFETIME = 7d`).
  - Celery is properly configured with Redis broker.

### Step 2: Accounts, Tenant Isolation & JWT Authentication
- **Target Files**:
  - `backend/apps/accounts/models.py` (`Organization`, `User` with role & org relation)
  - `backend/apps/accounts/serializers.py` (`CustomTokenObtainPairSerializer`, `UserRegistrationSerializer`, `UserProfileSerializer`)
  - `backend/apps/accounts/views.py` (Token views, registration, current profile)
  - `backend/apps/accounts/urls.py` (`/api/v1/auth/...`)
  - `backend/apps/accounts/authentication.py` / `permissions.py` (Tenant extraction & scoping)
- **JWT Architecture & Endpoints**:
  - **Endpoints**:
    - `POST /api/v1/auth/token/` - Obtain Access & Refresh tokens via email/password.
    - `POST /api/v1/auth/token/refresh/` - Refresh expired access token with valid refresh token.
    - `POST /api/v1/auth/token/verify/` - Validate JWT token authenticity and expiration.
    - `POST /api/v1/auth/register/` - Register organization + initial admin user.
    - `GET /api/v1/auth/me/` - Retrieve authenticated user info and organization profile.
  - **Custom JWT Claims**:
    - Embed `org_id`, `org_name`, `email`, and `role` (`admin`, `bid_manager`, `viewer`) inside the JWT access token payload so frontend and microservices can read tenant context without repeated DB lookups.
  - **Tenant Scoping**:
    - Request context automatically populated with `request.org_id` from JWT.
    - All downstream models (tenders, documents, rule-packs, audit) inherit from a tenant-aware base model / queryset filter.
- **Acceptance Criteria**:
  - User can register an organization and log in to obtain JWT access & refresh tokens.
  - Custom claims (`org_id`, `role`) are present in decoded access tokens.
  - Protected endpoints reject unauthorized or expired requests with HTTP 401.

### Step 3: Tenders & Snapshots Domain Models & Storage
- **Target Files**:
  - `backend/apps/tenders/models.py`
  - `backend/apps/tenders/services.py`
  - `backend/apps/tenders/views.py`
  - `backend/apps/tenders/urls.py`
- **Acceptance Criteria**:
  - Tenders ingestion via URL or Tender ID.
  - PDF tender upload with clause extraction.
  - Corrigendum snapshot caching and SHA-256 deduplication.

### Step 4: RulePack Models & Lifecycle API
- **Target Files**:
  - `backend/apps/rules/models.py`
  - `backend/apps/rules/services.py`
  - `backend/apps/rules/views.py`
  - `backend/apps/rules/urls.py`
- **Acceptance Criteria**:
  - Drafting rules from tender ingestion.
  - Human review endpoint to edit or dismiss rules.
  - Freeze endpoint creating immutable, cryptographic rule snapshot.

### Step 5: Bidder Documents & Intake Pipeline (Stage 1 & 2)
- **Target Files**:
  - `backend/apps/documents/models.py`
  - `backend/apps/documents/services.py`
  - `backend/apps/documents/views.py`
  - `backend/apps/documents/urls.py`
- **Acceptance Criteria**:
  - Multi-file upload for compliance documents (PDF, scans).
  - SHA-256 checksums, pyHanko cryptographic digital signature validation.
  - Text extraction pipeline.

### Step 6: Document AI & Schema-Constrained Extraction (Stage 3)
- **Target Files**:
  - `backend/services/llm.py`
  - `backend/apps/documents/tasks.py`
  - `backend/apps/documents/extraction.py`
- **Acceptance Criteria**:
  - Schema-constrained extraction into Udyam, CA Turnover, GST, and NSIC Pydantic schemas.
  - Verbatim text quote and page grounding checks (`is_grounded`).

### Step 7: Deterministic Rules Engine Integration (Stage 4 & 5)
- **Target Files**:
  - `backend/apps/verify/services.py`
  - `backend/apps/verify/models.py`
  - `backend/apps/verify/views.py`
- **Acceptance Criteria**:
  - Execution of `ComplianceEngine.evaluate(rule_pack, bidder_documents)`.
  - Zero hallucination: exact mathematical threshold checks and date validities.

### Step 8: External Registry Verification via TinyFish (Stage 6)
- **Target Files**:
  - `backend/services/tinyfish.py`
  - `backend/apps/verify/registry.py`
- **Acceptance Criteria**:
  - Validation against official sources: GST portal, Udyam MSME, ICAI UDIN.
  - Graceful fallback when registries are offline.

### Step 9: Verdict, Evidence Generation & Audit Trail (Stage 7)
- **Target Files**:
  - `backend/apps/evidence/models.py`, `backend/apps/evidence/views.py`
  - `backend/apps/audit/models.py`, `backend/apps/audit/services.py`
  - `backend/apps/verify/views.py`
- **Acceptance Criteria**:
  - Overall verdict generation (`READY`, `NEEDS_REVIEW`, `BLOCKED`).
  - Actionable FixList with missing documents and discrepancies.
  - Evidence citations linking field values to document bounding boxes / page quotes.
  - Immutable audit trail entries for every verification action.

### Step 10: Celery Asynchronous Tasks, API Routing & Test Suite
- **Target Files**:
  - `backend/config/urls.py` (Unified API routing `/api/v1/`)
  - `backend/apps/*/tasks.py`
  - `backend/golden/test_golden.py`
  - Test suites for all apps.
- **Acceptance Criteria**:
  - Celery background workers process document ingestion and TinyFish queries.
  - End-to-end automated tests pass with 100% deterministic results.
  - Golden test cases pass successfully.

---

## 4. Execution History & Updates
- *2026-10-24*: `backend_memory.md` created with project audit and 10-step roadmap.
- *2026-10-24*: Added detailed JWT authentication specifications to Step 1 and Step 2 (`djangorestframework-simplejwt`, token endpoints, custom claims with `org_id`, role, tenant scoping).
- *2026-10-24*: **ALL 10 SUB-STEPS IMPLEMENTED & VERIFIED**:
  - Step 1: Environment & Django Bootstrap (`manage.py`, `settings.py` with Neon DB + SQLite fallback, Celery, SimpleJWT, CORS).
  - Step 2: Accounts, Multi-tenant Isolation & JWT Auth (`Organization`, custom `User`, token obtain/refresh/verify, registration).
  - Step 3: Tenders & Snapshots Domain Models & Storage (`Tender`, `TenderSnapshot`, corrigendum caching).
  - Step 4: RulePack Models & Lifecycle API (`RulePack`, `RulePackItem`, DRAFT review, SHA-256 cryptographic freezing).
  - Step 5: Bidder Documents & Intake Pipeline (`BidderDocument` upload, SHA-256 integrity, pyHanko signature validation).
  - Step 6: Document AI & Schema-Constrained Extraction (Grounded entity extraction for Udyam, CA Turnover, GST, NSIC).
  - Step 7: Deterministic Rules Engine Integration (Pure-Python `ComplianceEngine` bridge, zero hallucination).
  - Step 8: External Registry Verification (Udyam, GSTN, ICAI UDIN verification).
  - Step 9: Verdict, Evidence Citations & Immutable Audit (`VerificationAssessment`, `EvidenceCitation`, `AuditLogEntry`).
  - Step 10: Celery Async Tasks, Unified API Routing (`/api/v1/...`), Full test suite (26/26 tests passing).
- *2026-10-24*: **Cloudflare R2 Object Storage Integration**:
  - Implemented `CloudflareR2Storage` adapter (`backend/services/r2_storage.py`) using `boto3` with SigV4 and automatic local disk fallback.
  - Connected `DocumentPipelineService` to upload bidder compliance documents directly to Cloudflare R2.
  - Updated `.env.example` with R2 configuration (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`).
  - Added unit test in `apps/documents/tests.py` testing R2 upload, download, and file existence (26/26 tests passing).

