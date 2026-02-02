"""Mailhog provider for email testing."""

from typing import Any

from testcontainers.core.generic import DockerContainer

from .base import ContainerProvider

# Default ports for Mailhog
SMTP_PORT = 1025
HTTP_PORT = 8025

# Django email backends that don't need Mailhog
SKIP_BACKENDS = (
    "django.core.mail.backends.console.EmailBackend",
    "django.core.mail.backends.filebased.EmailBackend",
    "django.core.mail.backends.locmem.EmailBackend",
    "django.core.mail.backends.dummy.EmailBackend",
)


class MailhogProvider(ContainerProvider):
    """Provider for Mailhog email testing containers."""

    @property
    def name(self) -> str:
        return "mailhog"

    def can_auto_detect(self, settings: Any, context: dict[str, Any] | None = None) -> bool:
        """Detect if SMTP email backend is configured.

        Uses original_email_backend from context when available, since Django's
        test setup overwrites EMAIL_BACKEND with locmem before detection runs.
        See: https://docs.djangoproject.com/en/5.2/topics/testing/tools/#email-services

        Mailhog should be used when:
        - EMAIL_BACKEND is smtp.EmailBackend (explicit)
        - EMAIL_BACKEND is not set (defaults to SMTP in Django)

        Mailhog should NOT be used when:
        - Console backend (prints to console)
        - File backend (writes to files)
        - In-memory backend (for testing without SMTP)
        - Dummy backend (discards emails)
        """
        if context and context.get("original_email_backend") is not None:
            email_backend = context["original_email_backend"]
        else:
            email_backend = getattr(settings, "EMAIL_BACKEND", None)

        # If no backend is set, Django defaults to SMTP, but we shouldn't auto-enable
        # Mailhog unless there's an explicit SMTP backend or EMAIL_HOST is configured
        if email_backend is None:
            # Check if there's explicit email configuration suggesting SMTP usage
            email_host = getattr(settings, "EMAIL_HOST", "")
            return bool(email_host)

        # Skip non-SMTP backends
        if email_backend in SKIP_BACKENDS:
            return False

        # Detect SMTP backend
        return bool(email_backend == "django.core.mail.backends.smtp.EmailBackend")

    def get_container(self, config: dict[str, Any]) -> DockerContainer:
        """Create Mailhog container with configuration."""
        image = config.get("image", "mailhog/mailhog:latest")

        container = DockerContainer(image).with_exposed_ports(SMTP_PORT, HTTP_PORT)

        env = config.get("environment", {})
        for key, value in env.items():
            container = container.with_env(key, value)

        return container

    def update_settings(
        self, container: DockerContainer, settings: Any, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Update email settings with container connection info."""
        host = container.get_container_host_ip()
        smtp_port = container.get_exposed_port(SMTP_PORT)
        http_port = container.get_exposed_port(HTTP_PORT)

        updates: dict[str, Any] = {
            # Restore SMTP backend (Django's test setup may have set it to locmem)
            "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
            "EMAIL_HOST": host,
            "EMAIL_PORT": int(smtp_port),
            "EMAIL_USE_TLS": False,
            "EMAIL_USE_SSL": False,
            # Store the API URL for retrieving sent emails in tests
            "MAILHOG_API_URL": f"http://{host}:{http_port}/api/v2",
        }

        return updates

    def get_default_config(self) -> dict[str, Any]:
        return {
            "image": "mailhog/mailhog:latest",
        }
