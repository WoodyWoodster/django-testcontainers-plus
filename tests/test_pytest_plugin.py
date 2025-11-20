"""Tests for pytest plugin."""

from unittest.mock import Mock

from django.conf import settings as django_settings

from django_testcontainers_plus import pytest_plugin


class TestPytestPlugin:
    """Test pytest plugin functionality."""

    def test_apply_settings_updates_simple(self):
        """Test applying simple settings updates."""
        updates = {"TEST_SETTING": "test_value"}

        pytest_plugin._apply_settings_updates(updates)

        assert hasattr(django_settings, "TEST_SETTING")
        assert django_settings.TEST_SETTING == "test_value"
        assert "TEST_SETTING" in pytest_plugin._original_settings

    def test_apply_settings_updates_dict_merge(self):
        """Test applying dict settings with merge."""
        original_databases = getattr(django_settings, "DATABASES", {})
        if not isinstance(original_databases, dict):
            original_databases = {}

        updates = {
            "DATABASES": {
                "test_db": {
                    "ENGINE": "django.db.backends.postgresql",
                    "HOST": "localhost",
                }
            }
        }

        pytest_plugin._apply_settings_updates(updates)

        assert hasattr(django_settings, "DATABASES")
        assert "test_db" in django_settings.DATABASES
        assert django_settings.DATABASES["test_db"]["ENGINE"] == "django.db.backends.postgresql"

    def test_apply_settings_updates_preserves_original(self):
        """Test that original settings are preserved."""
        original_value = getattr(django_settings, "TEST_ORIGINAL", None)

        django_settings.TEST_ORIGINAL = "original"
        updates = {"TEST_ORIGINAL": "updated"}

        pytest_plugin._original_settings.clear()
        pytest_plugin._apply_settings_updates(updates)

        assert pytest_plugin._original_settings["TEST_ORIGINAL"] == "original"
        assert django_settings.TEST_ORIGINAL == "updated"

        if original_value is not None:
            django_settings.TEST_ORIGINAL = original_value
        elif hasattr(django_settings, "TEST_ORIGINAL"):
            delattr(django_settings, "TEST_ORIGINAL")

    def test_restore_settings(self):
        """Test restoring original settings."""
        pytest_plugin._original_settings = {
            "TEST_RESTORE": "original_value",
            "TEST_NEW": None,
        }

        django_settings.TEST_RESTORE = "updated_value"
        django_settings.TEST_NEW = "new_value"

        pytest_plugin._restore_settings()

        assert django_settings.TEST_RESTORE == "original_value"
        assert pytest_plugin._original_settings == {}

    def test_restore_settings_empty(self):
        """Test restoring when no original settings exist."""
        pytest_plugin._original_settings.clear()

        pytest_plugin._restore_settings()

        assert pytest_plugin._original_settings == {}

    def test_container_manager_module_state(self):
        """Test that module-level container manager state works."""
        # Save original state
        original_manager = pytest_plugin._container_manager

        # Test setting and getting manager
        mock_manager = Mock()
        pytest_plugin._container_manager = mock_manager
        assert pytest_plugin._container_manager == mock_manager

        # Test None state
        pytest_plugin._container_manager = None
        assert pytest_plugin._container_manager is None

        # Restore original state
        pytest_plugin._container_manager = original_manager

    def test_apply_settings_updates_non_dict_original(self):
        """Test applying dict update when original setting is not a dict."""
        django_settings.NON_DICT_SETTING = "string_value"
        updates = {"NON_DICT_SETTING": {"key": "value"}}

        pytest_plugin._original_settings.clear()
        pytest_plugin._apply_settings_updates(updates)

        assert django_settings.NON_DICT_SETTING == {"key": "value"}
        assert pytest_plugin._original_settings["NON_DICT_SETTING"] == "string_value"

    def test_apply_settings_updates_multiple(self):
        """Test applying multiple settings updates."""
        updates = {
            "SETTING_ONE": "value_one",
            "SETTING_TWO": "value_two",
            "SETTING_THREE": {"nested": "value"},
        }

        pytest_plugin._original_settings.clear()
        pytest_plugin._apply_settings_updates(updates)

        assert django_settings.SETTING_ONE == "value_one"
        assert django_settings.SETTING_TWO == "value_two"
        assert django_settings.SETTING_THREE == {"nested": "value"}
        assert len(pytest_plugin._original_settings) == 3
