"""Utility functions shared between runner and pytest plugin."""

from typing import Any

from django.conf import settings
from django.db import connections


def apply_settings_updates(updates: dict[str, Any], original_settings: dict[str, Any]) -> None:
    """Apply settings updates and save originals for restoration.

    Args:
        updates: Dict of settings to update
        original_settings: Dict to store original values for later restoration
    """
    for key, value in updates.items():
        if key not in original_settings:
            original_settings[key] = getattr(settings, key, None)

        if isinstance(value, dict) and hasattr(settings, key):
            original = getattr(settings, key, {})
            if isinstance(original, dict):
                merged = {**original, **value}
                setattr(settings, key, merged)
            else:
                setattr(settings, key, value)
        else:
            setattr(settings, key, value)


def restore_settings(original_settings: dict[str, Any]) -> None:
    """Restore original settings values.

    Args:
        original_settings: Dict of original values to restore
    """
    for key, value in original_settings.items():
        setattr(settings, key, value)
    original_settings.clear()


def recreate_database_connections() -> None:
    """Recreate Django database connections with current settings.

    This is needed after updating DATABASES settings to ensure Django
    uses the new connection parameters instead of cached ones.
    """
    # Clear Django's cached connection settings
    if "settings" in connections.__dict__:
        del connections.__dict__["settings"]

    # Reconfigure connections with updated settings
    connections._settings = connections.configure_settings(settings.DATABASES)  # type: ignore[attr-defined]

    # Close all existing connections
    connections.close_all()

    # Explicitly recreate connections with new settings
    for alias in settings.DATABASES:
        connections[alias] = connections.create_connection(alias)
