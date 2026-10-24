"""
Celery asynchronous tasks for document ingestion, integrity, and extraction.
"""
import logging
from celery import shared_task
from apps.documents.services import DocumentPipelineService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_document_async(
    self,
    file_path: str,
    file_name: str,
    document_type: str,
    organization_id: str,
    tender_id: str = None,
):
    """Asynchronous background worker task for heavy PDF OCR and signature checking."""
    logger.info("Starting async document processing for %s (org: %s)", file_name, organization_id)
    try:
        pipeline = DocumentPipelineService()
        doc = pipeline.process_document(
            file_obj=file_path,
            file_name=file_name,
            document_type=document_type,
            organization_id=organization_id,
            tender_id=tender_id,
        )
        return {
            "success": True,
            "document_id": doc.id,
            "sha256_hash": doc.sha256_hash,
            "is_digitally_signed": doc.is_digitally_signed,
        }
    except Exception as exc:
        logger.error("Async document processing failed: %s", exc)
        raise self.retry(exc=exc, countdown=10)
