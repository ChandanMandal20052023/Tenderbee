"""
Cloudflare R2 / S3-compatible Object Storage Service for TenderBee.
Provides 100% S3-compatible API using boto3 with zero-cost egress support,
presigned URLs, and seamless local disk fallback for development.
"""
import io
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


class CloudflareR2Storage:
    """
    Cloudflare R2 Object Storage Adapter.
    Uses boto3 with S3-compatible endpoints, custom timeouts, and local disk fallback.
    """

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        region_name: str = "auto",
    ):
        # Read from arguments or environment
        account_id = os.getenv("R2_ACCOUNT_ID", "")
        default_endpoint = f"https://{account_id}.r2.cloudflarestorage.com" if account_id else ""

        self.endpoint_url = (
            endpoint_url
            or os.getenv("R2_ENDPOINT_URL")
            or os.getenv("S3_ENDPOINT_URL")
            or default_endpoint
        )
        self.access_key_id = (
            access_key_id
            or os.getenv("R2_ACCESS_KEY_ID")
            or os.getenv("S3_ACCESS_KEY_ID")
            or os.getenv("AWS_ACCESS_KEY_ID")
        )
        self.secret_access_key = (
            secret_access_key
            or os.getenv("R2_SECRET_ACCESS_KEY")
            or os.getenv("S3_SECRET_ACCESS_KEY")
            or os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.bucket_name = (
            bucket_name
            or os.getenv("R2_BUCKET_NAME")
            or os.getenv("S3_BUCKET_NAME")
            or os.getenv("AWS_STORAGE_BUCKET_NAME")
            or "tenderbee"
        )
        self.region_name = region_name or "auto"

        # Check if remote credentials are configured
        self.is_configured = bool(
            self.endpoint_url and self.access_key_id and self.secret_access_key
        )

        self._client = None
        if self.is_configured:
            try:
                # Cloudflare R2 standard boto3 configuration
                self._client = boto3.client(
                    "s3",
                    endpoint_url=self.endpoint_url,
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                    region_name=self.region_name,
                    config=Config(
                        signature_version="s3v4",
                        retries={"max_attempts": 3, "mode": "standard"},
                    ),
                )
                logger.info("Cloudflare R2 storage client initialized successfully.")
            except Exception as e:
                logger.warning("Failed to initialize Cloudflare R2 client: %s. Falling back to local disk.", e)
                self.is_configured = False
        else:
            logger.info("Cloudflare R2 credentials not set. Operating in local filesystem storage mode.")

    def upload_bytes(
        self,
        key: str,
        data: bytes,
        content_type: str = "application/pdf",
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Uploads in-memory bytes to Cloudflare R2 (or local fallback).
        Returns a dict with storage details, remote URL, or local path.
        """
        key = key.lstrip("/")
        if self.is_configured and self._client:
            try:
                extra_args = {"ContentType": content_type}
                if metadata:
                    extra_args["Metadata"] = metadata

                self._client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=data,
                    **extra_args,
                )
                remote_url = f"{self.endpoint_url}/{self.bucket_name}/{key}"
                return {
                    "backend": "cloudflare_r2",
                    "bucket": self.bucket_name,
                    "key": key,
                    "url": remote_url,
                    "success": True,
                }
            except Exception as e:
                logger.error("Failed to upload to Cloudflare R2 (%s): %s. Falling back to local disk.", key, e)

        # Fallback to local storage
        local_path = Path(settings.MEDIA_ROOT) / key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(data)

        return {
            "backend": "local_disk",
            "bucket": "local",
            "key": key,
            "path": str(local_path),
            "url": f"/media/{key}",
            "success": True,
        }

    def upload_file(
        self,
        key: str,
        file_path: Union[str, Path],
        content_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Uploads a local file to Cloudflare R2."""
        with open(file_path, "rb") as f:
            data = f.read()
        return self.upload_bytes(key=key, data=data, content_type=content_type or "application/octet-stream")

    def download_bytes(self, key: str) -> Optional[bytes]:
        """Downloads object bytes from Cloudflare R2 or local disk."""
        key = key.lstrip("/")
        if self.is_configured and self._client:
            try:
                response = self._client.get_object(Bucket=self.bucket_name, Key=key)
                return response["Body"].read()
            except ClientError as e:
                logger.warning("Object not found in Cloudflare R2: %s (%s)", key, e)
            except Exception as e:
                logger.error("Error downloading from Cloudflare R2: %s", e)

        # Check local disk
        local_path = Path(settings.MEDIA_ROOT) / key
        if local_path.exists():
            with open(local_path, "rb") as f:
                return f.read()
        return None

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> Optional[str]:
        """
        Generates a secure, temporary pre-signed download URL (valid for `expires_in` seconds).
        Cloudflare R2 has $0 egress fees, so downloads via presigned URLs are completely free.
        """
        key = key.lstrip("/")
        if self.is_configured and self._client:
            try:
                url = self._client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": key},
                    ExpiresIn=expires_in,
                )
                return url
            except Exception as e:
                logger.error("Failed to generate presigned URL for %s: %s", key, e)
        return None

    def file_exists(self, key: str) -> bool:
        """Checks if a file exists in Cloudflare R2 or local disk."""
        key = key.lstrip("/")
        if self.is_configured and self._client:
            try:
                self._client.head_object(Bucket=self.bucket_name, Key=key)
                return True
            except ClientError:
                pass

        local_path = Path(settings.MEDIA_ROOT) / key
        return local_path.exists()
