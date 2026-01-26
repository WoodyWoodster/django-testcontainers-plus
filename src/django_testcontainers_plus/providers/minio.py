"""MinIO (S3-compatible) container provider."""

from typing import Any

from testcontainers.core.generic import DockerContainer
from testcontainers.minio import MinioContainer

from .base import ContainerProvider


class MinioProvider(ContainerProvider):
    """Provider for MinIO (S3-compatible) containers.

    MinIO provides S3-compatible object storage for testing file uploads,
    static files, and media storage without requiring AWS credentials.

    Auto-detects from:
    - DEFAULT_FILE_STORAGE containing 's3' or 'minio'
    - STATICFILES_STORAGE containing 's3' or 'minio'
    - STORAGES dict (Django 4.2+) with S3 backends
    - AWS_STORAGE_BUCKET_NAME being set

    Configuration options:
    - image: Docker image (default: 'minio/minio:latest')
    - access_key: S3 access key (default: 'minioadmin')
    - secret_key: S3 secret key (default: 'minioadmin')
    - bucket_name: Default bucket name (default: 'test-bucket')
    - region: AWS region name (default: 'us-east-1')

    Example:
        TESTCONTAINERS = {
            'minio': {
                'image': 'minio/minio:latest',
                'access_key': 'test_key',
                'secret_key': 'test_secret',
                'bucket_name': 'my-test-bucket',
            }
        }
    """

    @property
    def name(self) -> str:
        return "minio"

    def can_auto_detect(self, settings: Any) -> bool:
        """Detect S3/MinIO usage from Django settings."""
        # Check DEFAULT_FILE_STORAGE
        default_storage = getattr(settings, "DEFAULT_FILE_STORAGE", "")
        if self._is_s3_storage(default_storage):
            return True

        # Check STATICFILES_STORAGE
        static_storage = getattr(settings, "STATICFILES_STORAGE", "")
        if self._is_s3_storage(static_storage):
            return True

        # Check STORAGES dict (Django 4.2+)
        storages = getattr(settings, "STORAGES", {})
        for storage_config in storages.values():
            if isinstance(storage_config, dict):
                backend = storage_config.get("BACKEND", "")
                if self._is_s3_storage(backend):
                    return True

        # Check for AWS S3 configuration
        if getattr(settings, "AWS_STORAGE_BUCKET_NAME", None):
            return True

        return False

    def _is_s3_storage(self, storage_class: str) -> bool:
        """Check if storage class is S3-related."""
        storage_lower = storage_class.lower()
        return any(
            pattern in storage_lower
            for pattern in [
                "s3boto3",
                "s3boto",
                "minio",
                "s3storage",
            ]
        )

    def get_container(self, config: dict[str, Any]) -> DockerContainer:
        """Create MinIO container with configuration."""
        image = config.get("image", "minio/minio:latest")
        access_key = config.get("access_key", "minioadmin")
        secret_key = config.get("secret_key", "minioadmin")

        container = MinioContainer(
            image=image,
            access_key=access_key,
            secret_key=secret_key,
        )

        # Add custom environment variables
        env = config.get("environment", {})
        for key, value in env.items():
            container = container.with_env(key, value)

        return container

    def update_settings(
        self, container: DockerContainer, settings: Any, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Update AWS/S3 settings with container connection info."""
        host = container.get_container_host_ip()
        port = container.get_exposed_port(9000)
        endpoint_url = f"http://{host}:{port}"

        access_key = config.get("access_key", "minioadmin")
        secret_key = config.get("secret_key", "minioadmin")
        bucket_name = config.get("bucket_name", "test-bucket")
        region = config.get("region", "us-east-1")

        # Allow custom settings override
        if "update_settings" in config:
            custom_settings = config["update_settings"]
            if isinstance(custom_settings, dict):
                return custom_settings

        updates: dict[str, Any] = {
            # Core AWS credentials
            "AWS_ACCESS_KEY_ID": access_key,
            "AWS_SECRET_ACCESS_KEY": secret_key,
            "AWS_S3_ENDPOINT_URL": endpoint_url,
            "AWS_STORAGE_BUCKET_NAME": bucket_name,
            "AWS_S3_REGION_NAME": region,
            # Common django-storages settings
            "AWS_S3_CUSTOM_DOMAIN": None,  # Disable CDN for testing
            "AWS_S3_SECURE_URLS": False,  # Use HTTP for local testing
            "AWS_QUERYSTRING_AUTH": False,  # Simpler URLs for testing
            "AWS_DEFAULT_ACL": None,  # Use bucket default
            # MinIO-specific settings
            "AWS_S3_SIGNATURE_VERSION": "s3v4",
            "AWS_S3_ADDRESSING_STYLE": "path",  # Required for MinIO
        }

        # Update STORAGES dict if present (Django 4.2+)
        storages = getattr(settings, "STORAGES", {})
        if storages:
            storages_updates: dict[str, Any] = {}
            for storage_name, storage_config in storages.items():
                if isinstance(storage_config, dict):
                    backend = storage_config.get("BACKEND", "")
                    if self._is_s3_storage(backend):
                        existing_options = storage_config.get("OPTIONS", {})
                        storages_updates[storage_name] = {
                            **storage_config,
                            "OPTIONS": {
                                **existing_options,
                                "endpoint_url": endpoint_url,
                                "access_key": access_key,
                                "secret_key": secret_key,
                                "bucket_name": bucket_name,
                                "region_name": region,
                            },
                        }
            if storages_updates:
                updates["STORAGES"] = storages_updates

        return updates

    def get_default_config(self) -> dict[str, Any]:
        """Get default configuration for MinIO provider."""
        return {
            "image": "minio/minio:latest",
            "access_key": "minioadmin",
            "secret_key": "minioadmin",
            "bucket_name": "test-bucket",
            "region": "us-east-1",
        }
