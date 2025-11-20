"""Tests for exception handling and helpful error messages."""

from unittest.mock import patch

import pytest

from django_testcontainers_plus.exceptions import (
    DjangoTestcontainersError,
    MissingDependencyError,
)
from django_testcontainers_plus.manager import ContainerManager


class MockSettings:
    """Mock Django settings object."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestMissingDependencyError:
    """Test MissingDependencyError exception."""

    def test_error_is_testcontainers_error(self):
        """Test that MissingDependencyError is a DjangoTestcontainersError."""
        error = MissingDependencyError("MySQL", "mysql")
        assert isinstance(error, DjangoTestcontainersError)

    def test_error_message_basic(self):
        """Test basic error message."""
        error = MissingDependencyError("MySQL", "mysql")
        message = str(error)

        assert "MySQL Support Not Installed" in message
        assert "pip install django-testcontainers-plus[mysql]" in message
        assert "pip install django-testcontainers-plus[all]" in message

    def test_error_message_with_detection(self):
        """Test error message includes detection location."""
        error = MissingDependencyError(
            "MySQL", "mysql", detected_in="DATABASES['default']['ENGINE']"
        )
        message = str(error)

        assert "MySQL was detected in your Django settings" in message
        assert "DATABASES['default']['ENGINE']" in message

    def test_error_message_with_original_error(self):
        """Test error message includes original error."""
        original = ImportError("No module named 'MySQLdb'")
        error = MissingDependencyError("MySQL", "mysql", original_error=original)
        message = str(error)

        assert "Original error:" in message
        assert "No module named 'MySQLdb'" in message

    def test_error_attributes(self):
        """Test error attributes are set correctly."""
        original = ImportError("test")
        error = MissingDependencyError(
            "Redis",
            "redis",
            detected_in="CACHES['default']",
            original_error=original,
        )

        assert error.provider_name == "Redis"
        assert error.extra_name == "redis"
        assert error.detected_in == "CACHES['default']"
        assert error.original_error == original


class TestContainerManagerErrorHandling:
    """Test ContainerManager raises helpful errors for unavailable providers."""

    @patch("django_testcontainers_plus.manager.UNAVAILABLE_PROVIDERS")
    def test_mysql_detection_raises_error(self, mock_unavailable):
        """Test MySQL detection raises helpful error when deps missing."""
        mock_unavailable.__bool__ = lambda self: True
        mock_unavailable.items = lambda: [
            ("mysql", ("mysql", ImportError("No module named 'MySQLdb'")))
        ]

        settings = MockSettings(DATABASES={"default": {"ENGINE": "django.db.backends.mysql"}})
        manager = ContainerManager(settings)

        with pytest.raises(MissingDependencyError) as exc_info:
            manager.detect_needed_containers()

        error = exc_info.value
        assert "MYSQL" in str(error)
        assert "pip install django-testcontainers-plus[mysql]" in str(error)
        assert "DATABASES['default']['ENGINE']" in str(error)

    @patch("django_testcontainers_plus.manager.UNAVAILABLE_PROVIDERS")
    def test_redis_cache_detection_raises_error(self, mock_unavailable):
        """Test Redis cache detection raises helpful error."""
        mock_unavailable.__bool__ = lambda self: True
        mock_unavailable.items = lambda: [
            ("redis", ("redis", ImportError("No module named 'redis'")))
        ]

        settings = MockSettings(
            CACHES={"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache"}}
        )
        manager = ContainerManager(settings)

        with pytest.raises(MissingDependencyError) as exc_info:
            manager.detect_needed_containers()

        error = exc_info.value
        assert "Redis" in str(error)
        assert "pip install django-testcontainers-plus[redis]" in str(error)
        assert "CACHES['default']['BACKEND']" in str(error)

    @patch("django_testcontainers_plus.manager.UNAVAILABLE_PROVIDERS")
    def test_redis_celery_detection_raises_error(self, mock_unavailable):
        """Test Redis Celery detection raises helpful error."""
        mock_unavailable.__bool__ = lambda self: True
        mock_unavailable.items = lambda: [
            ("redis", ("redis", ImportError("No module named 'redis'")))
        ]

        settings = MockSettings(CELERY_BROKER_URL="redis://localhost:6379/0")
        manager = ContainerManager(settings)

        with pytest.raises(MissingDependencyError) as exc_info:
            manager.detect_needed_containers()

        error = exc_info.value
        assert "Redis" in str(error)
        assert "CELERY_BROKER_URL" in str(error)

    @patch("django_testcontainers_plus.manager.UNAVAILABLE_PROVIDERS")
    def test_explicitly_enabled_provider_raises_error(self, mock_unavailable):
        """Test explicitly enabled unavailable provider raises error."""
        mock_unavailable.__bool__ = lambda self: True
        mock_unavailable.items = lambda: [
            ("redis", ("redis", ImportError("No module named 'redis'")))
        ]

        settings = MockSettings(TESTCONTAINERS={"redis": {"enabled": True}})
        manager = ContainerManager(settings)

        with pytest.raises(MissingDependencyError) as exc_info:
            manager.detect_needed_containers()

        error = exc_info.value
        assert "Redis" in str(error)
        assert "TESTCONTAINERS['redis']" in str(error)

    @patch("django_testcontainers_plus.manager.UNAVAILABLE_PROVIDERS")
    def test_no_error_when_provider_not_detected(self, mock_unavailable):
        """Test no error when unavailable provider is not needed."""
        mock_unavailable.__bool__ = lambda self: True
        mock_unavailable.items = lambda: [
            ("mysql", ("mysql", ImportError("No module named 'MySQLdb'")))
        ]

        # PostgreSQL settings, MySQL not needed
        settings = MockSettings(DATABASES={"default": {"ENGINE": "django.db.backends.postgresql"}})
        manager = ContainerManager(settings)

        # Should not raise
        providers = manager.detect_needed_containers()
        assert len(providers) >= 0  # May have PostgreSQL

    @patch("django_testcontainers_plus.manager.UNAVAILABLE_PROVIDERS")
    def test_no_error_when_auto_disabled(self, mock_unavailable):
        """Test no error when auto-detection is disabled for unavailable provider."""
        mock_unavailable.__bool__ = lambda self: True
        mock_unavailable.items = lambda: [
            ("mysql", ("mysql", ImportError("No module named 'MySQLdb'")))
        ]

        settings = MockSettings(
            DATABASES={"default": {"ENGINE": "django.db.backends.mysql"}},
            TESTCONTAINERS={"mysql": {"auto": False, "enabled": False}},
        )
        manager = ContainerManager(settings)

        # Should not raise because auto-detection is disabled
        providers = manager.detect_needed_containers()
        assert len(providers) >= 0
