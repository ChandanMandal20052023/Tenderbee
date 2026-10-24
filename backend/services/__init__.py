"""
Service layer adapters for TenderBee (TinyFish scraper, S3/database storage, LLM adapter).
"""
from backend.services.tinyfish import BidEasyScraper
from backend.services.storage import TenderStorage

__all__ = ["BidEasyScraper", "TenderStorage"]
