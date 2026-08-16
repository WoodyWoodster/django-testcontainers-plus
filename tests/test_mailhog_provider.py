"""Tests for MailhogProvider."""

from unittest.mock import Mock, patch

from django_testcontainers_plus.providers.mailhog import MailhogProvider
from tests.helpers import MockSettings


class TestMailhogProvider:
    """Test MailhogProvider class."""

    def test_name(self):
        """Test provider name."""
        provider = MailhogProvider()
        assert provider.name == "mailhog"

    def test_can_auto_detect_smtp_backend(self):
        """Test auto-detection with explicit SMTP backend."""
        settings = MockSettings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_with_email_host_no_backend(self):
        """Test auto-detection when EMAIL_HOST is set but no backend specified."""
        settings = MockSettings(EMAIL_HOST="localhost")
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_no_email_config(self):
        """Test auto-detection without any email configuration."""
        settings = MockSettings()
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_console_backend(self):
        """Test that console backend is skipped."""
        settings = MockSettings(EMAIL_BACKEND="django.core.mail.backends.console.EmailBackend")
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_file_backend(self):
        """Test that file backend is skipped."""
        settings = MockSettings(EMAIL_BACKEND="django.core.mail.backends.filebased.EmailBackend")
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_locmem_backend(self):
        """Test that in-memory backend is skipped."""
        settings = MockSettings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_dummy_backend(self):
        """Test that dummy backend is skipped."""
        settings = MockSettings(EMAIL_BACKEND="django.core.mail.backends.dummy.EmailBackend")
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_custom_backend(self):
        """Test that custom third-party backends are not auto-detected."""
        settings = MockSettings(EMAIL_BACKEND="anymail.backends.sendgrid.EmailBackend")
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_uses_context_over_settings(self):
        """Test that context original_email_backend is used over settings.

        Django's test setup overwrites EMAIL_BACKEND to locmem. The context
        provides the original value captured before the overwrite.
        """
        # Settings reflect Django's test override (locmem)
        settings = MockSettings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
        # Context provides the original value (smtp)
        context = {
            "original_email_backend": "django.core.mail.backends.smtp.EmailBackend",
        }
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings, context) is True

    def test_can_auto_detect_context_with_non_smtp_original(self):
        """Test that context with non-SMTP original backend is skipped."""
        settings = MockSettings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
        context = {
            "original_email_backend": "django.core.mail.backends.console.EmailBackend",
        }
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings, context) is False

    def test_can_auto_detect_context_with_no_original_backend(self):
        """Test fallback to EMAIL_HOST when context has None original backend."""
        settings = MockSettings(EMAIL_HOST="localhost")
        context = {"original_email_backend": None}
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings, context) is True

    def test_can_auto_detect_empty_context_falls_back_to_settings(self):
        """Test that empty context falls back to reading settings directly."""
        settings = MockSettings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings, context={}) is True

    def test_can_auto_detect_mailers_smtp_backend(self):
        """Test auto-detection from Django 6.1 MAILERS smtp backend."""
        settings = MockSettings(
            MAILERS={
                "default": {
                    "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                    "OPTIONS": {"host": "smtp.example.com"},
                }
            }
        )
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_mailers_host_no_backend(self):
        """Test auto-detection when MAILERS OPTIONS host is set without BACKEND."""
        settings = MockSettings(
            MAILERS={
                "default": {
                    "OPTIONS": {"host": "smtp.example.com"},
                }
            }
        )
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_mailers_locmem_backend(self):
        """Test that MAILERS locmem backend is skipped."""
        settings = MockSettings(
            MAILERS={
                "default": {
                    "BACKEND": "django.core.mail.backends.locmem.EmailBackend",
                }
            }
        )
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_mailers_console_backend(self):
        """Test that MAILERS console backend is skipped."""
        settings = MockSettings(
            MAILERS={
                "default": {
                    "BACKEND": "django.core.mail.backends.console.EmailBackend",
                }
            }
        )
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_uses_context_mailers_over_settings(self):
        """Test that context original_mailers is used over overwritten settings."""
        settings = MockSettings(
            MAILERS={
                "default": {
                    "BACKEND": "django.core.mail.backends.locmem.EmailBackend",
                }
            }
        )
        context = {
            "original_mailers": {
                "default": {
                    "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                    "OPTIONS": {"host": "smtp.example.com"},
                }
            }
        }
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings, context) is True

    def test_can_auto_detect_mailers_takes_precedence_over_email_backend(self):
        """Test that MAILERS backend is preferred over EMAIL_BACKEND."""
        settings = MockSettings(
            EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
            MAILERS={
                "default": {
                    "BACKEND": "django.core.mail.backends.console.EmailBackend",
                }
            },
        )
        provider = MailhogProvider()

        assert provider.can_auto_detect(settings) is False

    @patch("django_testcontainers_plus.providers.mailhog.DockerContainer")
    def test_get_container_defaults(self, mock_docker_container):
        """Test container creation with default config."""
        provider = MailhogProvider()
        config = {}

        mock_container_instance = Mock()
        mock_container_instance.with_exposed_ports = Mock(return_value=mock_container_instance)
        mock_docker_container.return_value = mock_container_instance

        container = provider.get_container(config)

        mock_docker_container.assert_called_once_with("mailhog/mailhog:latest")
        mock_container_instance.with_exposed_ports.assert_called_once_with(1025, 8025)
        assert container == mock_container_instance

    @patch("django_testcontainers_plus.providers.mailhog.DockerContainer")
    def test_get_container_custom_image(self, mock_docker_container):
        """Test container creation with custom image."""
        provider = MailhogProvider()
        config = {"image": "mailhog/mailhog:v1.0.1"}

        mock_container_instance = Mock()
        mock_container_instance.with_exposed_ports = Mock(return_value=mock_container_instance)
        mock_docker_container.return_value = mock_container_instance

        provider.get_container(config)

        mock_docker_container.assert_called_once_with("mailhog/mailhog:v1.0.1")

    @patch("django_testcontainers_plus.providers.mailhog.DockerContainer")
    def test_get_container_with_environment(self, mock_docker_container):
        """Test container creation with environment variables."""
        provider = MailhogProvider()
        config = {
            "environment": {
                "MH_STORAGE": "maildir",
                "MH_MAILDIR_PATH": "/maildir",
            }
        }

        mock_container_instance = Mock()
        mock_container_instance.with_exposed_ports = Mock(return_value=mock_container_instance)
        mock_container_instance.with_env = Mock(return_value=mock_container_instance)
        mock_docker_container.return_value = mock_container_instance

        provider.get_container(config)

        assert mock_container_instance.with_env.call_count == 2
        mock_container_instance.with_env.assert_any_call("MH_STORAGE", "maildir")
        mock_container_instance.with_env.assert_any_call("MH_MAILDIR_PATH", "/maildir")

    def test_update_settings(self):
        """Test settings update with container connection info."""
        settings = MockSettings(
            EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend",
            EMAIL_HOST="localhost",
            EMAIL_PORT=25,
        )

        provider = MailhogProvider()
        config = {}

        mock_container = Mock()
        mock_container.get_container_host_ip = Mock(return_value="127.0.0.1")
        port_map = {1025: 32768, 8025: 32769}
        mock_container.get_exposed_port = Mock(side_effect=lambda p: port_map[p])

        updates = provider.update_settings(mock_container, settings, config)

        assert updates["EMAIL_HOST"] == "127.0.0.1"
        assert updates["EMAIL_PORT"] == 32768
        assert updates["EMAIL_USE_TLS"] is False
        assert updates["EMAIL_USE_SSL"] is False
        assert updates["MAILHOG_API_URL"] == "http://127.0.0.1:32769/api/v2"

    def test_update_settings_port_type(self):
        """Test that EMAIL_PORT is an integer."""
        settings = MockSettings()

        provider = MailhogProvider()
        config = {}

        mock_container = Mock()
        mock_container.get_container_host_ip = Mock(return_value="localhost")
        # Simulate string port (as returned by some container implementations)
        port_map = {1025: "1025", 8025: "8025"}
        mock_container.get_exposed_port = Mock(side_effect=lambda p: port_map[p])

        updates = provider.update_settings(mock_container, settings, config)

        assert isinstance(updates["EMAIL_PORT"], int)
        assert updates["EMAIL_PORT"] == 1025

    def test_update_settings_with_mailers(self):
        """Test that MAILERS is patched instead of deprecated EMAIL_* keys."""
        settings = MockSettings(
            MAILERS={
                "default": {
                    "BACKEND": "django.core.mail.backends.locmem.EmailBackend",
                },
                "marketing": {
                    "BACKEND": "example.third.party.EmailBackend",
                },
            }
        )

        provider = MailhogProvider()
        mock_container = Mock()
        mock_container.get_container_host_ip = Mock(return_value="127.0.0.1")
        port_map = {1025: 32768, 8025: 32769}
        mock_container.get_exposed_port = Mock(side_effect=lambda p: port_map[p])

        updates = provider.update_settings(mock_container, settings, {})

        assert "EMAIL_BACKEND" not in updates
        assert "EMAIL_HOST" not in updates
        assert updates["MAILERS"]["default"]["BACKEND"] == (
            "django.core.mail.backends.smtp.EmailBackend"
        )
        assert updates["MAILERS"]["default"]["OPTIONS"]["host"] == "127.0.0.1"
        assert updates["MAILERS"]["default"]["OPTIONS"]["port"] == 32768
        assert updates["MAILERS"]["default"]["OPTIONS"]["use_tls"] is False
        assert updates["MAILERS"]["default"]["OPTIONS"]["use_ssl"] is False
        assert updates["MAILHOG_API_URL"] == "http://127.0.0.1:32769/api/v2"
        assert "marketing" not in updates["MAILERS"]

    def test_update_settings_mailers_port_type(self):
        """Test that MAILERS OPTIONS port is an integer."""
        settings = MockSettings(
            MAILERS={
                "default": {
                    "BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                }
            }
        )

        provider = MailhogProvider()
        mock_container = Mock()
        mock_container.get_container_host_ip = Mock(return_value="localhost")
        port_map = {1025: "1025", 8025: "8025"}
        mock_container.get_exposed_port = Mock(side_effect=lambda p: port_map[p])

        updates = provider.update_settings(mock_container, settings, {})

        assert isinstance(updates["MAILERS"]["default"]["OPTIONS"]["port"], int)
        assert updates["MAILERS"]["default"]["OPTIONS"]["port"] == 1025

    def test_get_default_config(self):
        """Test default configuration."""
        provider = MailhogProvider()
        config = provider.get_default_config()

        assert config == {
            "image": "mailhog/mailhog:latest",
        }
