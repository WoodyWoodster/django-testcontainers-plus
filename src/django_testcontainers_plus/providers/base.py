from abc import ABC, abstractmethod
from typing import Any

from testcontainers.core.generic import DockerContainer


class ContainerProvider(ABC):
    """Base class for all container providers.

    Each provider is responsible for:
    1. Detecting if the service is needed from Django settings
    2. Creating and configuring the container
    3. Providing settings updates with container connection info
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this provider."""
        ...

    @abstractmethod
    def can_auto_detect(self, settings: Any) -> bool:
        """Check if this service is needed based on Django settings.

        Args:
            settings: Django settings module

        Returns:
            True if this service should be automatically started
        """
        ...

    @abstractmethod
    def get_container(self, config: dict[str, Any]) -> DockerContainer:
        """Create and configure the container.

        Args:
            config: Configuration dict from TESTCONTAINERS setting

        Returns:
            Configured testcontainer instance
        """
        ...

    @abstractmethod
    def update_settings(
        self, container: DockerContainer, settings: Any, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate settings updates with container connection info.

        Args:
            container: Running container instance
            settings: Django settings module
            config: Configuration dict from TESTCONTAINERS setting

        Returns:
            Dict of settings updates to apply
        """
        ...

    def get_default_config(self) -> dict[str, Any]:
        """Get default configuration for this provider.

        Returns:
            Default configuration dict
        """
        return {}
