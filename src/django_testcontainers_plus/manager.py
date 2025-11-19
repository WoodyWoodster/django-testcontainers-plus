"""Container manager for orchestrating test containers."""

from typing import Any, Dict, List

from testcontainers.core.generic import DockerContainer

from .providers import PROVIDER_REGISTRY, ContainerProvider


class ContainerManager:
    """Manages lifecycle of test containers."""

    def __init__(self, settings: Any):
        """Initialize container manager.

        Args:
            settings: Django settings module
        """
        self.settings = settings
        self.providers: List[ContainerProvider] = PROVIDER_REGISTRY
        self.active_containers: Dict[str, DockerContainer] = {}
        self.settings_updates: Dict[str, Any] = {}

    def get_testcontainers_config(self) -> Dict[str, Any]:
        """Get TESTCONTAINERS configuration from settings.

        Returns:
            Configuration dict, empty if not defined
        """
        return getattr(self.settings, "TESTCONTAINERS", {})

    def detect_needed_containers(self) -> List[ContainerProvider]:
        """Detect which containers are needed based on settings.

        Returns:
            List of providers that should be started
        """
        config = self.get_testcontainers_config()
        needed_providers = []

        for provider in self.providers:
            provider_config = config.get(provider.name, {})

            # Check if explicitly enabled/disabled
            if "enabled" in provider_config:
                if provider_config["enabled"]:
                    needed_providers.append(provider)
                continue

            # Check if auto-detection is disabled
            if provider_config.get("auto", True) is False:
                continue

            # Auto-detect if the service is needed
            if provider.can_auto_detect(self.settings):
                needed_providers.append(provider)

        # Also check for explicitly configured providers not in auto-detect
        for provider_name in config.keys():
            provider_config = config[provider_name]
            if provider_config.get("enabled", True):
                # Find the provider
                provider = next((p for p in self.providers if p.name == provider_name), None)
                if provider and provider not in needed_providers:
                    needed_providers.append(provider)

        return needed_providers

    def start_containers(self) -> Dict[str, Any]:
        """Start all needed containers.

        Returns:
            Dict of settings updates to apply
        """
        needed_providers = self.detect_needed_containers()
        config = self.get_testcontainers_config()
        all_updates = {}

        for provider in needed_providers:
            # Get provider config with defaults
            provider_config = {
                **provider.get_default_config(),
                **config.get(provider.name, {}),
            }

            # Create and start container
            container = provider.get_container(provider_config)
            container.start()

            # Store reference
            self.active_containers[provider.name] = container

            # Get settings updates
            updates = provider.update_settings(container, self.settings, provider_config)

            # Merge updates
            self._merge_updates(all_updates, updates)

        self.settings_updates = all_updates
        return all_updates

    def stop_containers(self) -> None:
        """Stop and remove all active containers."""
        for container in self.active_containers.values():
            try:
                container.stop()
            except Exception:
                # Best effort cleanup
                pass

        self.active_containers.clear()

    def _merge_updates(self, target: Dict[str, Any], updates: Dict[str, Any]) -> None:
        """Deep merge settings updates.

        Args:
            target: Target dict to merge into
            updates: Updates to merge
        """
        for key, value in updates.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Deep merge dicts
                self._merge_updates(target[key], value)
            else:
                target[key] = value
