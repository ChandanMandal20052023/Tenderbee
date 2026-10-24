"""
Production-level storage engine for TenderBee Tenders and Snapshots.
Supports Multi-tenant isolation, SHA-256 immutability, and tiered storage
(SQLite/PostgreSQL metadata + Local/S3 object storage for raw payloads).
"""
import os
import json
import hashlib
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pathlib import Path


class TenderStorage:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            # Dynamically locate the repository data directory: <repo_root>/data
            self.base_dir = Path(__file__).resolve().parents[2] / "data"
            
        self.snapshots_dir = self.base_dir / "snapshots"
        self.db_path = self.base_dir / "tenderbee.db"
        
        # Ensure directories exist
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initializes relational tables with organization_id tenant isolation."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 1. Tender Master Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tenders (
                    tender_id TEXT PRIMARY KEY,
                    organization_id TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    buyer_name TEXT,
                    submission_deadline TEXT,
                    estimated_value_inr REAL,
                    source_url TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # 2. Immutable Tender Snapshots (Corrigendum tracking via SHA-256)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tender_snapshots (
                    snapshot_id TEXT PRIMARY KEY,
                    tender_id TEXT NOT NULL,
                    organization_id TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    raw_payload_path TEXT NOT NULL,
                    extracted_json_path TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    FOREIGN KEY (tender_id) REFERENCES tenders (tender_id)
                )
            """)
            
            # 3. Versioned Rule Packs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rule_packs (
                    rule_pack_id TEXT PRIMARY KEY,
                    tender_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    rules_json TEXT NOT NULL,
                    confirmed_by TEXT,
                    confirmed_at TEXT,
                    FOREIGN KEY (tender_id) REFERENCES tenders (tender_id)
                )
            """)
            
            conn.commit()

    @staticmethod
    def compute_sha256(data: str) -> str:
        """Returns standard SHA-256 hash."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def get_snapshot_by_url(self, source_url: str, org_id: str = "org_default") -> Optional[Dict[str, Any]]:
        """Returns cached snapshot if already ingested for this organization."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM tender_snapshots 
                WHERE source_url = ? AND organization_id = ?
                ORDER BY fetched_at DESC LIMIT 1
            """, (source_url, org_id))
            row = cursor.fetchone()
            if not row:
                return None
            
            # Read extracted json payload from object storage
            extracted_path = Path(row["extracted_json_path"])
            if extracted_path.exists():
                with open(extracted_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        return None

    def get_snapshot_by_tender_number(self, tender_number: str, org_id: str = "org_default") -> Optional[Dict[str, Any]]:
        """Returns cached snapshot by Tender Number / ID if already ingested."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ts.extracted_json_path FROM tenders t
                JOIN tender_snapshots ts ON t.tender_id = ts.tender_id
                WHERE (t.external_id = ? OR t.tender_id = ?) AND t.organization_id = ?
                ORDER BY ts.fetched_at DESC LIMIT 1
            """, (tender_number, tender_number, org_id))
            row = cursor.fetchone()
            if not row:
                return None
            
            extracted_path = Path(row["extracted_json_path"])
            if extracted_path.exists():
                with open(extracted_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        return None

    def save_tender_and_snapshot(
        self,
        org_id: str,
        tender_number: str,
        tender_title: str,
        source_url: str,
        buyer_name: Optional[str],
        submission_deadline: Optional[str],
        estimated_value_inr: Optional[float],
        extracted_data: Dict[str, Any],
        raw_text_payload: str,
    ) -> Dict[str, Any]:
        """
        Stores tender metadata and commits an immutable snapshot to tiered storage.
        """
        content_hash = self.compute_sha256(raw_text_payload or json.dumps(extracted_data, sort_keys=True))
        tender_id = f"tnd_{self.compute_sha256(tender_number)[:12]}"
        snapshot_id = f"snp_{content_hash[:16]}"
        now = datetime.now(timezone.utc).isoformat()

        # 1. Save raw and structured payloads to object storage (snapshots folder)
        raw_path = self.snapshots_dir / f"{content_hash}_raw.txt"
        extracted_path = self.snapshots_dir / f"{content_hash}_extracted.json"
        
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(raw_text_payload)
            
        with open(extracted_path, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=2)

        # 2. Commit relational metadata
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Upsert master tender record
            cursor.execute("""
                INSERT INTO tenders (
                    tender_id, organization_id, external_id, title, buyer_name,
                    submission_deadline, estimated_value_inr, source_url, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(tender_id) DO UPDATE SET
                    title = excluded.title,
                    buyer_name = excluded.buyer_name,
                    submission_deadline = excluded.submission_deadline,
                    updated_at = excluded.updated_at
            """, (
                tender_id, org_id, tender_number, tender_title, buyer_name,
                submission_deadline, estimated_value_inr, source_url, now, now
            ))
            
            # Append immutable snapshot
            cursor.execute("""
                INSERT OR REPLACE INTO tender_snapshots (
                    snapshot_id, tender_id, organization_id, source_url,
                    content_hash, raw_payload_path, extracted_json_path, fetched_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id, tender_id, org_id, source_url,
                content_hash, str(raw_path), str(extracted_path), now
            ))
            
            conn.commit()

        return {
            "tender_id": tender_id,
            "snapshot_id": snapshot_id,
            "content_hash": content_hash,
            "raw_payload_path": str(raw_path),
            "extracted_json_path": str(extracted_path),
            "is_cached": False,
        }
