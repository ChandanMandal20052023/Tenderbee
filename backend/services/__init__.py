"""
Service layer adapters for TenderBee (TinyFish scraper, S3/database storage, LLM adapter).
"""
from backend.services.tinyfish import BidEasyScraper
from backend.services.storage import TenderStorage
from backend.services.captcha import CaptchaService
from backend.services.session_pool import PortalSessionPool
from backend.services.gepnic import GePNICAdapter
from backend.services.gem import GeMAdapter
from backend.services.scraper import UniversalTenderScraper

__all__ = [
    "UniversalTenderScraper",
    "BidEasyScraper",
    "TenderStorage",
    "CaptchaService",
    "PortalSessionPool",
    "GePNICAdapter",
    "GeMAdapter",
]
