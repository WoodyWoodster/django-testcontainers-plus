"""Tests for MinIO provider."""

from unittest.mock import Mock, patch

import pytest

from django_testcontainers_plus.providers.minio import MinioProvider


class TestMinioProviderName:
    """Tests for MinIO provider name."""

    def test_name_is_minio(self) -> None:
        """Provider name should be 'minio'."""
        provider = MinioProvider()
        assert provider.name == "minio"


class TestMinioProviderAutoDetect:
    """Tests for MinIO auto-detection."""

    def test_can_auto_detect_s3boto3_storage(self) -> None:
        """Should detect django-storages S3Boto3Storage."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None

        provider = MinioProvider()
        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_s3boto_storage(self) -> None:
        """Should detect older S3BotoStorage."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = "storages.backends.s3boto.S3BotoStorage"
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None

        provider = MinioProvider()
        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_staticfiles_storage(self) -> None:
        """Should detect S3 staticfiles storage."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = ""
        settings.STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None

        provider = MinioProvider()
        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_storages_dict_default(self) -> None:
        """Should detect S3 in STORAGES dict default backend."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = ""
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {
            "default": {
                "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
            }
        }
        settings.AWS_STORAGE_BUCKET_NAME = None

        provider = MinioProvider()
        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_storages_dict_staticfiles(self) -> None:
        """Should detect S3 in STORAGES dict staticfiles backend."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = ""
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {
            "staticfiles": {
                "BACKEND": "storages.backends.s3boto3.S3StaticStorage",
            }
        }
        settings.AWS_STORAGE_BUCKET_NAME = None

        provider = MinioProvider()
        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_aws_bucket_name(self) -> None:
        """Should detect when AWS_STORAGE_BUCKET_NAME is set."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = ""
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = "my-bucket"

        provider = MinioProvider()
        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_minio_storage(self) -> None:
        """Should detect custom MinIO storage backend."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = "myapp.storage.MinioStorage"
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None

        provider = MinioProvider()
        assert provider.can_auto_detect(settings) is True

    def test_no_auto_detect_filesystem_storage(self) -> None:
        """Should not detect FileSystemStorage."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
        settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None

        provider = MinioProvider()
        assert provider.can_auto_detect(settings) is False

    def test_no_auto_detect_empty_settings(self) -> None:
        """Should not detect when no storage settings present."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = ""
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None

        provider = MinioProvider()
        assert provider.can_auto_detect(settings) is False

    def test_no_auto_detect_no_attributes(self) -> None:
        """Should not detect when settings attributes don't exist."""
        settings = Mock(spec=[])  # No attributes

        provider = MinioProvider()
        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_uses_context_default_file_storage(self) -> None:
        """Should use original_default_file_storage from context over settings."""
        settings = Mock()
        # Settings have been modified (e.g., by test framework)
        settings.DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None

        # Context preserves the original S3 value
        context = {
            "original_default_file_storage": "storages.backends.s3boto3.S3Boto3Storage",
        }

        provider = MinioProvider()
        assert provider.can_auto_detect(settings, context) is True

    def test_can_auto_detect_uses_context_staticfiles_storage(self) -> None:
        """Should use original_staticfiles_storage from context over settings."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = ""
        settings.STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None

        context = {
            "original_staticfiles_storage": "storages.backends.s3boto3.S3StaticStorage",
        }

        provider = MinioProvider()
        assert provider.can_auto_detect(settings, context) is True

    def test_can_auto_detect_uses_context_storages_dict(self) -> None:
        """Should use original_storages from context over settings."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = ""
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {}  # Modified by test framework
        settings.AWS_STORAGE_BUCKET_NAME = None

        context = {
            "original_storages": {
                "default": {
                    "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
                }
            },
        }

        provider = MinioProvider()
        assert provider.can_auto_detect(settings, context) is True

    def test_can_auto_detect_uses_context_aws_bucket_name(self) -> None:
        """Should use original_aws_storage_bucket_name from context over settings."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = ""
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None  # Cleared by test framework

        context = {
            "original_aws_storage_bucket_name": "my-production-bucket",
        }

        provider = MinioProvider()
        assert provider.can_auto_detect(settings, context) is True

    def test_can_auto_detect_empty_context_falls_back_to_settings(self) -> None:
        """Should fall back to settings when context is empty."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None

        provider = MinioProvider()
        assert provider.can_auto_detect(settings, context={}) is True

    def test_can_auto_detect_context_with_none_value_falls_back(self) -> None:
        """Should fall back to settings when context value is None."""
        settings = Mock()
        settings.DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
        settings.STATICFILES_STORAGE = ""
        settings.STORAGES = {}
        settings.AWS_STORAGE_BUCKET_NAME = None

        context = {"original_default_file_storage": None}

        provider = MinioProvider()
        assert provider.can_auto_detect(settings, context) is True


class TestMinioProviderContainer:
    """Tests for MinIO container creation."""

    def test_get_container_defaults(self) -> None:
        """Should create container with default config."""
        provider = MinioProvider()
        config = provider.get_default_config()

        with patch(
            "django_testcontainers_plus.providers.minio.MinioContainer"
        ) as mock_container:
            mock_instance = Mock()
            mock_container.return_value = mock_instance

            result = provider.get_container(config)

            mock_container.assert_called_once_with(
                image="minio/minio:latest",
                access_key="minioadmin",
                secret_key="minioadmin",
            )
            assert result == mock_instance

    def test_get_container_custom_image(self) -> None:
        """Should create container with custom image."""
        provider = MinioProvider()
        config = {
            "image": "minio/minio:RELEASE.2024-01-01",
            "access_key": "minioadmin",
            "secret_key": "minioadmin",
        }

        with patch(
            "django_testcontainers_plus.providers.minio.MinioContainer"
        ) as mock_container:
            mock_instance = Mock()
            mock_container.return_value = mock_instance

            provider.get_container(config)

            mock_container.assert_called_once_with(
                image="minio/minio:RELEASE.2024-01-01",
                access_key="minioadmin",
                secret_key="minioadmin",
            )

    def test_get_container_custom_credentials(self) -> None:
        """Should create container with custom credentials."""
        provider = MinioProvider()
        config = {
            "image": "minio/minio:latest",
            "access_key": "custom_access_key",
            "secret_key": "custom_secret_key",
        }

        with patch(
            "django_testcontainers_plus.providers.minio.MinioContainer"
        ) as mock_container:
            mock_instance = Mock()
            mock_container.return_value = mock_instance

            provider.get_container(config)

            mock_container.assert_called_once_with(
                image="minio/minio:latest",
                access_key="custom_access_key",
                secret_key="custom_secret_key",
            )

    def test_get_container_with_environment(self) -> None:
        """Should add environment variables to container."""
        provider = MinioProvider()
        config = {
            "image": "minio/minio:latest",
            "access_key": "minioadmin",
            "secret_key": "minioadmin",
            "environment": {
                "MINIO_BROWSER": "off",
                "MINIO_CONSOLE_ADDRESS": ":9001",
            },
        }

        with patch(
            "django_testcontainers_plus.providers.minio.MinioContainer"
        ) as mock_container:
            mock_instance = Mock()
            mock_instance.with_env.return_value = mock_instance
            mock_container.return_value = mock_instance

            provider.get_container(config)

            assert mock_instance.with_env.call_count == 2


class TestMinioProviderSettings:
    """Tests for MinIO settings updates."""

    def test_update_settings_basic(self) -> None:
        """Should update AWS settings with container info."""
        provider = MinioProvider()
        container = Mock()
        container.get_container_host_ip.return_value = "localhost"
        container.get_exposed_port.return_value = "9000"

        settings = Mock()
        settings.STORAGES = {}

        config = provider.get_default_config()
        updates = provider.update_settings(container, settings, config)

        assert updates["AWS_ACCESS_KEY_ID"] == "minioadmin"
        assert updates["AWS_SECRET_ACCESS_KEY"] == "minioadmin"
        assert updates["AWS_S3_ENDPOINT_URL"] == "http://localhost:9000"
        assert updates["AWS_STORAGE_BUCKET_NAME"] == "test-bucket"
        assert updates["AWS_S3_REGION_NAME"] == "us-east-1"
        assert updates["AWS_S3_SIGNATURE_VERSION"] == "s3v4"
        assert updates["AWS_S3_ADDRESSING_STYLE"] == "path"

    def test_update_settings_custom_bucket(self) -> None:
        """Should use custom bucket name."""
        provider = MinioProvider()
        container = Mock()
        container.get_container_host_ip.return_value = "localhost"
        container.get_exposed_port.return_value = "9000"

        settings = Mock()
        settings.STORAGES = {}

        config = {**provider.get_default_config(), "bucket_name": "custom-bucket"}
        updates = provider.update_settings(container, settings, config)

        assert updates["AWS_STORAGE_BUCKET_NAME"] == "custom-bucket"

    def test_update_settings_custom_region(self) -> None:
        """Should use custom region."""
        provider = MinioProvider()
        container = Mock()
        container.get_container_host_ip.return_value = "localhost"
        container.get_exposed_port.return_value = "9000"

        settings = Mock()
        settings.STORAGES = {}

        config = {**provider.get_default_config(), "region": "eu-west-1"}
        updates = provider.update_settings(container, settings, config)

        assert updates["AWS_S3_REGION_NAME"] == "eu-west-1"

    def test_update_settings_custom_credentials(self) -> None:
        """Should use custom credentials in settings."""
        provider = MinioProvider()
        container = Mock()
        container.get_container_host_ip.return_value = "localhost"
        container.get_exposed_port.return_value = "9000"

        settings = Mock()
        settings.STORAGES = {}

        config = {
            **provider.get_default_config(),
            "access_key": "custom_key",
            "secret_key": "custom_secret",
        }
        updates = provider.update_settings(container, settings, config)

        assert updates["AWS_ACCESS_KEY_ID"] == "custom_key"
        assert updates["AWS_SECRET_ACCESS_KEY"] == "custom_secret"

    def test_update_settings_storages_dict(self) -> None:
        """Should update STORAGES dict with S3 backends."""
        provider = MinioProvider()
        container = Mock()
        container.get_container_host_ip.return_value = "localhost"
        container.get_exposed_port.return_value = "9000"

        settings = Mock()
        settings.STORAGES = {
            "default": {
                "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
                "OPTIONS": {"file_overwrite": False},
            },
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        }

        config = provider.get_default_config()
        updates = provider.update_settings(container, settings, config)

        # Should update only S3 storage
        assert "STORAGES" in updates
        assert "default" in updates["STORAGES"]
        assert "staticfiles" not in updates["STORAGES"]

        # Should preserve existing options and add new ones
        default_options = updates["STORAGES"]["default"]["OPTIONS"]
        assert default_options["file_overwrite"] is False
        assert default_options["endpoint_url"] == "http://localhost:9000"
        assert default_options["access_key"] == "minioadmin"
        assert default_options["bucket_name"] == "test-bucket"

    def test_update_settings_custom_override(self) -> None:
        """Should use custom update_settings when provided."""
        provider = MinioProvider()
        container = Mock()
        container.get_container_host_ip.return_value = "localhost"
        container.get_exposed_port.return_value = "9000"

        settings = Mock()
        settings.STORAGES = {}

        custom_settings = {"CUSTOM_SETTING": "custom_value"}
        config = {**provider.get_default_config(), "update_settings": custom_settings}
        updates = provider.update_settings(container, settings, config)

        assert updates == custom_settings

    def test_update_settings_different_port(self) -> None:
        """Should use actual exposed port."""
        provider = MinioProvider()
        container = Mock()
        container.get_container_host_ip.return_value = "192.168.1.100"
        container.get_exposed_port.return_value = "32768"

        settings = Mock()
        settings.STORAGES = {}

        config = provider.get_default_config()
        updates = provider.update_settings(container, settings, config)

        assert updates["AWS_S3_ENDPOINT_URL"] == "http://192.168.1.100:32768"


class TestMinioProviderDefaultConfig:
    """Tests for MinIO default configuration."""

    def test_default_config_values(self) -> None:
        """Should have expected default values."""
        provider = MinioProvider()
        config = provider.get_default_config()

        assert config["image"] == "minio/minio:latest"
        assert config["access_key"] == "minioadmin"
        assert config["secret_key"] == "minioadmin"
        assert config["bucket_name"] == "test-bucket"
        assert config["region"] == "us-east-1"

    def test_default_config_keys(self) -> None:
        """Should have all expected keys."""
        provider = MinioProvider()
        config = provider.get_default_config()

        expected_keys = {"image", "access_key", "secret_key", "bucket_name", "region"}
        assert set(config.keys()) == expected_keys
