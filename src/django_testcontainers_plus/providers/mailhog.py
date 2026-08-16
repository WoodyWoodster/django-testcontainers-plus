"""Mailhog provider for email testing."""

from typing import Any

from testcontainers.core.generic import DockerContainer

from .base import ContainerProvider

# Default ports for Mailhog
SMTP_PORT = 1025
HTTP_PORT = 8025

SMTP_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Django email backends that don't need Mailhog
SKIP_BACKENDS = (
    "django.core.mail.backends.console.EmailBackend",
    "django.core.mail.backends.filebased.EmailBackend",
    "django.core.mail.backends.locmem.EmailBackend",
    "django.core.mail.backends.dummy.EmailBackend",
)


def _mailers_default(mailers: Any) -> dict[str, Any] | None:
    """Return the default mailer config if MAILERS is a dict with a default entry."""
    if not isinstance(mailers, dict):
        return None
    default = mailers.get("default")
    return default if isinstance(default, dict) else None


def _mailers_backend(mailers: Any) -> str | None:
    """Return BACKEND from MAILERS['default'], if set."""
    default = _mailers_default(mailers)
    if default is None:
        return None
    backend = default.get("BACKEND")
    return backend if isinstance(backend, str) else None


def _mailers_has_host(mailers: Any) -> bool:
    """Return True if MAILERS['default']['OPTIONS']['host'] is set."""
    default = _mailers_default(mailers)
    if default is None:
        return False
    options = default.get("OPTIONS") or {}
    return isinstance(options, dict) and bool(options.get("host"))


class MailhogProvider(ContainerProvider):
    """Provider for Mailhog email testing containers."""

    @property
    def name(self) -> str:
        return "mailhog"

    def can_auto_detect(self, settings: Any, context: dict[str, Any] | None = None) -> bool:
        """Detect if SMTP email backend is configured.

        Uses original values from context when available, since Django's test
        setup overwrites EMAIL_BACKEND (and MAILERS, when defined) with locmem
        before detection runs.
        See: https://docs.djangoproject.com/en/6.1/topics/testing/tools/#email-services

        Mailhog should be used when:
        - MAILERS['default']['BACKEND'] is smtp.EmailBackend (Django 6.1+)
        - EMAIL_BACKEND is smtp.EmailBackend (explicit)
        - No backend is set, but EMAIL_HOST or MAILERS OPTIONS host is configured

        Mailhog should NOT be used when:
        - Console backend (prints to console)
        - File backend (writes to files)
        - In-memory backend (for testing without SMTP)
        - Dummy backend (discards emails)
        """
        mailers = None
        email_backend = None

        if context:
            if context.get("original_mailers") is not None:
                mailers = context["original_mailers"]
            if context.get("original_email_backend") is not None:
                email_backend = context["original_email_backend"]

        if mailers is None:
            mailers = getattr(settings, "MAILERS", None)
        if email_backend is None:
            email_backend = getattr(settings, "EMAIL_BACKEND", None)

        backend = _mailers_backend(mailers)
        if backend is None:
            backend = email_backend

        if backend is None:
            return _mailers_has_host(mailers) or bool(getattr(settings, "EMAIL_HOST", ""))

        if backend in SKIP_BACKENDS:
            return False

        return backend == SMTP_BACKEND

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
        """Update email settings with container connection info.

        When MAILERS is defined (Django 6.1+), patch the default mailer OPTIONS
        instead of the deprecated EMAIL_* settings. Otherwise keep the EMAIL_*
        path for Django 5.2 / 6.0.
        """
        host = container.get_container_host_ip()
        smtp_port = int(container.get_exposed_port(SMTP_PORT))
        http_port = container.get_exposed_port(HTTP_PORT)

        updates: dict[str, Any] = {
            "MAILHOG_API_URL": f"http://{host}:{http_port}/api/v2",
        }

        mailers = getattr(settings, "MAILERS", None)
        if isinstance(mailers, dict) and mailers:
            default = dict(_mailers_default(mailers) or {})
            options = dict(default.get("OPTIONS") or {})
            options.update(
                {
                    "host": host,
                    "port": smtp_port,
                    "use_tls": False,
                    "use_ssl": False,
                }
            )
            updates["MAILERS"] = {
                "default": {
                    **default,
                    "BACKEND": SMTP_BACKEND,
                    "OPTIONS": options,
                }
            }
            return updates

        updates.update(
            {
                # Restore SMTP backend (Django's test setup may have set it to locmem)
                "EMAIL_BACKEND": SMTP_BACKEND,
                "EMAIL_HOST": host,
                "EMAIL_PORT": smtp_port,
                "EMAIL_USE_TLS": False,
                "EMAIL_USE_SSL": False,
            }
        )
        return updates

    def get_default_config(self) -> dict[str, Any]:
        return {
            "image": "mailhog/mailhog:latest",
        }
