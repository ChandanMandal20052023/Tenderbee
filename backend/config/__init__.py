"""
Django config package initialization.
"""
from backend.config.celery import app as celery_app

__all__ = ("celery_app",)
