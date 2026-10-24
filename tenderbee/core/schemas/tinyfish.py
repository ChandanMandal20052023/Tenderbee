"""Schemas for TinyFish Fetch, Search, and Agent API integrations."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class TinyFishFetchRequest(BaseModel):
    """Request payload to fetch one or more URLs via TinyFish."""
    urls: List[str] = Field(..., max_length=10, description="List of allow-listed URLs (max 10)")
    render_js: bool = Field(default=False, description="Whether to render JavaScript")
    ttl_seconds: int = Field(default=86400, description="Cache TTL in seconds")
    etag: Optional[str] = Field(default=None, description="Optional ETag for conditional fetching")


class TinyFishFetchItem(BaseModel):
    """Result of fetching an individual URL."""
    source_url: str = Field(...)
    final_url: Optional[str] = Field(default=None)
    status_code: int = Field(...)
    content_type: Optional[str] = Field(default=None)
    text_content: Optional[str] = Field(default=None, description="Extracted clean text content")
    markdown_content: Optional[str] = Field(default=None, description="Markdown formatted content")
    raw_content_base64: Optional[str] = Field(default=None, description="For PDF documents")
    content_hash: str = Field(..., description="SHA-256 hash of fetched payload")
    fetched_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = Field(default=None, description="Per-URL error if fetch failed")


class TinyFishFetchResponse(BaseModel):
    """Batch response from TinyFish Fetch API."""
    items: List[TinyFishFetchItem] = Field(default_factory=list)
    total_requested: int
    successful_count: int


class TinyFishSearchRequest(BaseModel):
    """Search request to locate tender notices across allow-listed portals."""
    query: str = Field(..., min_length=3, description="Tender ID, title, or search term")
    domain_filter: Optional[List[str]] = Field(
        default=["eprocure.gov.in", "gem.gov.in"],
        description="Allow-listed domains to constrain search"
    )
    max_results: int = Field(default=5, ge=1, le=20)


class TinyFishSearchItem(BaseModel):
    """Single candidate tender result returned by TinyFish Search."""
    title: str = Field(...)
    url: str = Field(...)
    snippet: str = Field(...)
    domain: str = Field(...)


class TinyFishSearchResponse(BaseModel):
    """List of candidate tenders found."""
    results: List[TinyFishSearchItem] = Field(default_factory=list)


class TinyFishUdyamAgentResult(BaseModel):
    """Expected schema for TinyFish Agent Udyam official verification."""
    udyam_number: str
    enterprise_name: Optional[str] = None
    enterprise_type: Optional[str] = None
    nic_codes: List[str] = Field(default_factory=list)
    is_active: bool = False
    status_text: Optional[str] = None
    captcha_encountered: bool = False
    otp_required: bool = False
    error: Optional[str] = None
