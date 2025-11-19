"""Pytest plugin for testcontainers integration with pytest-django."""

from typing import Any, Dict, Generator

import pytest
from django.conf import settings

from .manager import ContainerManager

# Global container manager instance
_container_manager: ContainerManager = None
_original_settings: Dict[str, Any] = {}


@pytest.fixture(scope="session", autouse=True)
def django_testcontainers_setup(
    django_db_setup: Any,
) -> Generator[ContainerManager, None, None]:
    """Automatically start and stop testcontainers for the test session.

    This fixture:
    1. Runs before any tests
    2. Detects needed containers from Django settings
    3. Starts the containers
    4. Updates Django settings with connection info
    5. Cleans up containers after all tests complete

    Args:
        django_db_setup: pytest-django fixture that sets up databases

    Yields:
        ContainerManager instance with active containers
    """
    global _container_manager, _original_settings

    # Initialize container manager
    _container_manager = ContainerManager(settings)

    # Start containers and get settings updates
    settings_updates = _container_manager.start_containers()

    # Apply settings updates
    _apply_settings_updates(settings_updates)

    # Print what was started
    for provider_name in _container_manager.active_containers.keys():
        print(f"Started {provider_name} container for testing")

    # Yield for tests to run
    yield _container_manager

    # Cleanup: restore settings and stop containers
    _restore_settings()
    print("Stopping test containers...")
    _container_manager.stop_containers()


@pytest.fixture(scope="session")
def testcontainers_manager() -> ContainerManager:
    """Get the active container manager.

    Returns:
        ContainerManager instance with active containers
    """
    return _container_manager


def _apply_settings_updates(updates: Dict[str, Any]) -> None:
    """Apply settings updates and save originals for restoration.

    Args:
        updates: Dict of settings to update
    """
    global _original_settings

    for key, value in updates.items():
        # Save original value
        if key not in _original_settings:
            _original_settings[key] = getattr(settings, key, None)

        # Apply update
        if isinstance(value, dict) and hasattr(settings, key):
            # Deep merge for dict settings like DATABASES, CACHES
            original = getattr(settings, key, {})
            if isinstance(original, dict):
                merged = {**original, **value}
                setattr(settings, key, merged)
            else:
                setattr(settings, key, value)
        else:
            setattr(settings, key, value)


def _restore_settings() -> None:
    """Restore original settings values."""
    global _original_settings

    for key, value in _original_settings.items():
        setattr(settings, key, value)
    _original_settings.clear()


# Register the plugin
pytest_plugins = ["django_testcontainers_plus.pytest_plugin"]
