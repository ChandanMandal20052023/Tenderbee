"""
Celery asynchronous tasks for Tender scraping and PDF parsing.
"""
import logging
from celery import shared_task
from apps.tenders.services import TenderService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def intake_tender_async(
    self,
    identifier: str,
    organization_id: str = "org_default",
    force_refresh: bool = False,
):
    """Background task for web portal scraping and initial rulepack drafting."""
    logger.info("Executing async tender intake for '%s' (org: %s)", identifier, organization_id)
    try:
        service = TenderService()
        result = service.intake_tender(
            identifier=identifier,
            org_id=organization_id,
            force_refresh=force_refresh,
        )
        return result
    except Exception as exc:
        logger.error("Async tender intake failed: %s", exc)
        raise self.retry(exc=exc, countdown=15)
