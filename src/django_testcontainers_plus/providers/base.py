"""Base container provider interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

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
        pass

    @abstractmethod
    def can_auto_detect(self, settings: Any) -> bool:
        """Check if this service is needed based on Django settings.

        Args:
            settings: Django settings module

        Returns:
            True if this service should be automatically started
        """
        pass

    @abstractmethod
    def get_container(self, config: Dict[str, Any]) -> DockerContainer:
        """Create and configure the container.

        Args:
            config: Configuration dict from TESTCONTAINERS setting

        Returns:
            Configured testcontainer instance
        """
        pass

    @abstractmethod
    def update_settings(
        self, container: DockerContainer, settings: Any, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate settings updates with container connection info.

        Args:
            container: Running container instance
            settings: Django settings module
            config: Configuration dict from TESTCONTAINERS setting

        Returns:
            Dict of settings updates to apply
        """
        pass

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for this provider.

        Returns:
            Default configuration dict
        """
        return {}
