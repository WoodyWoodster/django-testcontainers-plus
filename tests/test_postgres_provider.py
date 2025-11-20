"""Tests for PostgresProvider."""

from unittest.mock import Mock, patch

from django_testcontainers_plus.providers.postgres import PostgresProvider


class MockSettings:
    """Mock Django settings object."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestPostgresProvider:
    """Test PostgresProvider class."""

    def test_name(self):
        """Test provider name."""
        provider = PostgresProvider()
        assert provider.name == "postgres"

    def test_can_auto_detect_postgresql_engine(self):
        """Test auto-detection with postgresql engine."""
        settings = MockSettings(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                }
            }
        )
        provider = PostgresProvider()

        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_psycopg_engine(self):
        """Test auto-detection with psycopg engine."""
        settings = MockSettings(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.postgresql_psycopg2",
                }
            }
        )
        provider = PostgresProvider()

        assert provider.can_auto_detect(settings) is True

    def test_can_auto_detect_no_postgresql(self):
        """Test auto-detection without postgresql."""
        settings = MockSettings(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                }
            }
        )
        provider = PostgresProvider()

        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_no_databases(self):
        """Test auto-detection without DATABASES setting."""
        settings = MockSettings()
        provider = PostgresProvider()

        assert provider.can_auto_detect(settings) is False

    def test_can_auto_detect_multiple_databases(self):
        """Test auto-detection with multiple databases."""
        settings = MockSettings(
            DATABASES={
                "default": {"ENGINE": "django.db.backends.sqlite3"},
                "postgres_db": {"ENGINE": "django.db.backends.postgresql"},
            }
        )
        provider = PostgresProvider()

        assert provider.can_auto_detect(settings) is True

    @patch("django_testcontainers_plus.providers.postgres.PostgresContainer")
    def test_get_container_defaults(self, mock_postgres_container):
        """Test container creation with default config."""
        provider = PostgresProvider()
        config = {}

        mock_container_instance = Mock()
        mock_postgres_container.return_value = mock_container_instance

        container = provider.get_container(config)

        mock_postgres_container.assert_called_once_with(
            image="postgres:16",
            username="test",
            password="test",
            dbname="test",
        )
        assert container == mock_container_instance

    @patch("django_testcontainers_plus.providers.postgres.PostgresContainer")
    def test_get_container_custom_config(self, mock_postgres_container):
        """Test container creation with custom config."""
        provider = PostgresProvider()
        config = {
            "image": "postgres:15-alpine",
            "username": "myuser",
            "password": "mypass",
            "dbname": "mydb",
        }

        mock_container_instance = Mock()
        mock_postgres_container.return_value = mock_container_instance

        provider.get_container(config)

        mock_postgres_container.assert_called_once_with(
            image="postgres:15-alpine",
            username="myuser",
            password="mypass",
            dbname="mydb",
        )

    @patch("django_testcontainers_plus.providers.postgres.PostgresContainer")
    def test_get_container_with_environment(self, mock_postgres_container):
        """Test container creation with environment variables."""
        provider = PostgresProvider()
        config = {
            "environment": {
                "POSTGRES_INITDB_ARGS": "--encoding=UTF-8",
                "TZ": "UTC",
            }
        }

        mock_container_instance = Mock()
        mock_container_instance.with_env = Mock(return_value=mock_container_instance)
        mock_postgres_container.return_value = mock_container_instance

        provider.get_container(config)

        assert mock_container_instance.with_env.call_count == 2
        mock_container_instance.with_env.assert_any_call("POSTGRES_INITDB_ARGS", "--encoding=UTF-8")
        mock_container_instance.with_env.assert_any_call("TZ", "UTC")

    def test_update_settings_single_database(self):
        """Test settings update for single PostgreSQL database."""
        settings = MockSettings(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": "mydb",
                }
            }
        )

        provider = PostgresProvider()
        config = {
            "username": "testuser",
            "password": "testpass",
            "dbname": "testdb",
        }

        mock_container = Mock()
        mock_container.get_container_host_ip = Mock(return_value="127.0.0.1")
        mock_container.get_exposed_port = Mock(return_value=5432)

        updates = provider.update_settings(mock_container, settings, config)

        assert "DATABASES" in updates
        assert "default" in updates["DATABASES"]
        assert updates["DATABASES"]["default"]["HOST"] == "127.0.0.1"
        assert updates["DATABASES"]["default"]["PORT"] == 5432
        assert updates["DATABASES"]["default"]["USER"] == "testuser"
        assert updates["DATABASES"]["default"]["PASSWORD"] == "testpass"
        assert updates["DATABASES"]["default"]["NAME"] == "testdb"
        assert updates["DATABASES"]["default"]["ENGINE"] == "django.db.backends.postgresql"

    def test_update_settings_multiple_databases(self):
        """Test settings update for multiple databases."""
        settings = MockSettings(
            DATABASES={
                "default": {"ENGINE": "django.db.backends.sqlite3"},
                "postgres": {"ENGINE": "django.db.backends.postgresql"},
                "other_postgres": {"ENGINE": "django.db.backends.postgresql_psycopg2"},
            }
        )

        provider = PostgresProvider()
        config = {"username": "test", "password": "test", "dbname": "test"}

        mock_container = Mock()
        mock_container.get_container_host_ip = Mock(return_value="localhost")
        mock_container.get_exposed_port = Mock(return_value=5555)

        updates = provider.update_settings(mock_container, settings, config)

        assert "DATABASES" in updates
        assert "default" not in updates["DATABASES"]
        assert "postgres" in updates["DATABASES"]
        assert "other_postgres" in updates["DATABASES"]
        assert updates["DATABASES"]["postgres"]["PORT"] == 5555
        assert updates["DATABASES"]["other_postgres"]["PORT"] == 5555

    def test_update_settings_no_postgresql_databases(self):
        """Test settings update when no PostgreSQL databases exist."""
        settings = MockSettings(
            DATABASES={
                "default": {"ENGINE": "django.db.backends.sqlite3"},
            }
        )

        provider = PostgresProvider()
        config = {"username": "test", "password": "test", "dbname": "test"}

        mock_container = Mock()
        mock_container.get_container_host_ip = Mock(return_value="localhost")
        mock_container.get_exposed_port = Mock(return_value=5432)

        updates = provider.update_settings(mock_container, settings, config)

        assert updates == {}

    def test_update_settings_preserves_existing_config(self):
        """Test that settings update preserves existing database config."""
        settings = MockSettings(
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": "original_name",
                    "ATOMIC_REQUESTS": True,
                    "CONN_MAX_AGE": 600,
                }
            }
        )

        provider = PostgresProvider()
        config = {"username": "test", "password": "test", "dbname": "test"}

        mock_container = Mock()
        mock_container.get_container_host_ip = Mock(return_value="127.0.0.1")
        mock_container.get_exposed_port = Mock(return_value=5432)

        updates = provider.update_settings(mock_container, settings, config)

        assert updates["DATABASES"]["default"]["ATOMIC_REQUESTS"] is True
        assert updates["DATABASES"]["default"]["CONN_MAX_AGE"] == 600
        assert updates["DATABASES"]["default"]["ENGINE"] == "django.db.backends.postgresql"

    def test_get_default_config(self):
        """Test default configuration."""
        provider = PostgresProvider()
        config = provider.get_default_config()

        assert config == {
            "image": "postgres:16",
            "username": "test",
            "password": "test",
            "dbname": "test",
        }
