from typing import Any, Dict, Generator

import pytest
from django.conf import settings

from .manager import ContainerManager

_container_manager: ContainerManager | None = None
_original_settings: dict[str, Any] = {}


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

    _container_manager = ContainerManager(settings)

    settings_updates = _container_manager.start_containers()

    _apply_settings_updates(settings_updates)

    for provider_name in _container_manager.active_containers.keys():
        print(f"Started {provider_name} container for testing")

    yield _container_manager

    _restore_settings()
    print("Stopping test containers...")
    _container_manager.stop_containers()


@pytest.fixture(scope="session")
def testcontainers_manager() -> ContainerManager | None:
    """Get the active container manager.

    Returns:
        ContainerManager instance with active containers
    """
    return _container_manager


def _apply_settings_updates(updates: dict[str, Any]) -> None:
    """Apply settings updates and save originals for restoration.

    Args:
        updates: Dict of settings to update
    """
    global _original_settings

    for key, value in updates.items():
        if key not in _original_settings:
            _original_settings[key] = getattr(settings, key, None)

        if isinstance(value, dict) and hasattr(settings, key):
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


pytest_plugins = ["django_testcontainers_plus.pytest_plugin"]
