from typing import Any

from django.conf import settings
from django.test.runner import DiscoverRunner

from .manager import ContainerManager
from .utils import apply_settings_updates, recreate_database_connections, restore_settings


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
        self.container_manager: ContainerManager | None = None
        self.original_settings: dict[str, Any] = {}

    def setup_test_environment(self, **kwargs: Any) -> None:
        """Set up test environment and start containers."""
        # Capture original settings before Django's setup_test_environment
        # overwrites them (e.g. EMAIL_BACKEND is set to locmem)
        context = {
            "original_email_backend": getattr(settings, "EMAIL_BACKEND", None),
        }

        super().setup_test_environment(**kwargs)

        self.container_manager = ContainerManager(settings, context=context)

        settings_updates = self.container_manager.start_containers()

        if settings_updates:
            apply_settings_updates(settings_updates, self.original_settings)
            recreate_database_connections()

        if self.verbosity >= 1:
            for provider_name in self.container_manager.active_containers.keys():
                print(f"Started {provider_name} container for testing")

    def teardown_test_environment(self, **kwargs: Any) -> None:
        """Tear down test environment and stop containers."""
        restore_settings(self.original_settings)

        if self.container_manager:
            if self.verbosity >= 1:
                print("Stopping test containers...")
            self.container_manager.stop_containers()

        super().teardown_test_environment(**kwargs)
