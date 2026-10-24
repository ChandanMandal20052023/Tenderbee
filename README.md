# TenderBee

Intelligent Tender Platform comprising three modules:
- **Find**: Tender discovery and eligibility fit
- **Verify**: Document verification and bid-readiness
- **Prepare**: Proposal and bid-document maker

All three modules share four core capabilities:
1. Human-confirmed rule pack per tender
2. Machine-verified evidence per fact
3. Pure-Python deterministic rules engine (`core/engine`)
4. Immutable, append-only audit trail (`backend/audit`)

## Neon Serverless Database Configuration
> **Important Note on Database Connections:**
> - **Runtime Application**: Runs against the pooled connection string (`DATABASE_URL`) to leverage connection pooling. Django settings enforce a short `conn_max_age` (e.g. 0 to 60 seconds) because Neon serverless compute instances suspend when idle.
> - **Database Migrations**: Migrations must run against the direct connection string (`DIRECT_URL`) because schema migrations require session-level locking and are incompatible with transaction-mode poolers. Use `make migrate`.
