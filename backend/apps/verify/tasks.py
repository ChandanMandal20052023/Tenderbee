"""
Celery asynchronous tasks for heavy Verification pipeline evaluations.
"""
import logging
from celery import shared_task
from apps.verify.services import VerificationService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def evaluate_compliance_async(
    self,
    tender_id: str,
    organization_id: str,
    rule_pack_id: str = None,
    actor: str = "celery_worker",
):
    """Background task evaluating deterministic compliance rules and external registries."""
    logger.info("Executing async compliance evaluation for tender %s (org: %s)", tender_id, organization_id)
    try:
        service = VerificationService()
        result = service.run_assessment(
            tender_id=tender_id,
            organization_id=organization_id,
            rule_pack_id=rule_pack_id,
            actor=actor,
        )
        return result
    except Exception as exc:
        logger.error("Async compliance assessment failed: %s", exc)
        raise self.retry(exc=exc, countdown=10)
