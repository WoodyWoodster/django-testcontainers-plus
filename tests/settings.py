"""
Django settings for testing django-testcontainers-plus.
"""

SECRET_KEY = "test-secret-key-for-django-testcontainers-plus"

DEBUG = True

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Default auto field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Test runner configuration
TEST_RUNNER = "django_testcontainers_plus.TestcontainersRunner"

# Testcontainers configuration for tests
TESTCONTAINERS_PROVIDERS = {
    "postgres": {
        "provider": "django_testcontainers_plus.PostgresProvider",
        "image": "postgres:16-alpine",
        "database_name": "test_db",
        "username": "test_user",
        "password": "test_password",
    },
}

USE_TZ = True
