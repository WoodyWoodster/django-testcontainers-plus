"""Django test runner with testcontainers integration."""

from typing import Any, Dict, List, Optional

from django.conf import settings
from django.test.runner import DiscoverRunner

from .manager import ContainerManager


class TestcontainersRunner(DiscoverRunner):
    """Django test runner that automatically manages testcontainers.

    This runner extends Django's DiscoverRunner to automatically:
    1. Detect needed containers from settings
    2. Start containers before test databases are set up
    3. Update database settings with container connection info
    4. Clean up containers after tests complete

    Usage:
        # settings.py
        TEST_RUNNER = 'django_testcontainers_plus.runner.TestcontainersRunner'

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': 'test',
            }
        }
    """

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize the test runner."""
        super().__init__(*args, **kwargs)
        self.container_manager: Optional[ContainerManager] = None
        self.original_settings: Dict[str, Any] = {}

    def setup_test_environment(self, **kwargs: Any) -> None:
        """Set up test environment and start containers."""
        super().setup_test_environment(**kwargs)

        # Initialize container manager
        self.container_manager = ContainerManager(settings)

        # Start containers and get settings updates
        settings_updates = self.container_manager.start_containers()

        # Apply settings updates
        self._apply_settings_updates(settings_updates)

        # Log what was started
        if self.verbosity >= 1:
            for provider_name in self.container_manager.active_containers.keys():
                print(f"Started {provider_name} container for testing")

    def teardown_test_environment(self, **kwargs: Any) -> None:
        """Tear down test environment and stop containers."""
        # Restore original settings
        self._restore_settings()

        # Stop containers
        if self.container_manager:
            if self.verbosity >= 1:
                print("Stopping test containers...")
            self.container_manager.stop_containers()

        super().teardown_test_environment(**kwargs)

    def _apply_settings_updates(self, updates: Dict[str, Any]) -> None:
        """Apply settings updates and save originals for restoration.

        Args:
            updates: Dict of settings to update
        """
        for key, value in updates.items():
            # Save original value
            if key not in self.original_settings:
                self.original_settings[key] = getattr(settings, key, None)

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

    def _restore_settings(self) -> None:
        """Restore original settings values."""
        for key, value in self.original_settings.items():
            setattr(settings, key, value)
        self.original_settings.clear()
