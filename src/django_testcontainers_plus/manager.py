from typing import Any

from testcontainers.core.generic import DockerContainer

from .exceptions import MissingDependencyError
from .providers import PROVIDER_REGISTRY, UNAVAILABLE_PROVIDERS, ContainerProvider


class ContainerManager:
    """Manages lifecycle of test containers."""

    def __init__(self, settings: Any):
        """Initialize container manager.

        Args:
            settings: Django settings module
        """
        self.settings = settings
        self.providers: list[ContainerProvider] = PROVIDER_REGISTRY
        self.active_containers: dict[str, DockerContainer] = {}
        self.settings_updates: dict[str, Any] = {}

    def get_testcontainers_config(self) -> dict[str, Any]:
        """Get TESTCONTAINERS configuration from settings.

        Returns:
            Configuration dict, empty if not defined
        """
        return getattr(self.settings, "TESTCONTAINERS", {})

    def detect_needed_containers(self) -> list[ContainerProvider]:
        """Detect which containers are needed based on settings.

        Returns:
            List of providers that should be started

        Raises:
            MissingDependencyError: If a needed provider is unavailable
        """
        config = self.get_testcontainers_config()
        needed_providers = []

        for provider in self.providers:
            provider_config = config.get(provider.name, {})

            if "enabled" in provider_config:
                if provider_config["enabled"]:
                    needed_providers.append(provider)
                continue

            if provider_config.get("auto", True) is False:
                continue

            if provider.can_auto_detect(self.settings):
                needed_providers.append(provider)

        for provider_name in config.keys():
            provider_config = config[provider_name]
            if provider_config.get("enabled", True):
                found_provider: ContainerProvider | None = next(
                    (p for p in self.providers if p.name == provider_name), None
                )
                if found_provider is not None and found_provider not in needed_providers:
                    needed_providers.append(found_provider)

        self._check_unavailable_providers()

        return needed_providers

    def start_containers(self) -> dict[str, Any]:
        """Start all needed containers.

        Returns:
            Dict of settings updates to apply
        """
        needed_providers = self.detect_needed_containers()
        config = self.get_testcontainers_config()
        all_updates: dict[str, Any] = {}

        for provider in needed_providers:
            provider_config = {
                **provider.get_default_config(),
                **config.get(provider.name, {}),
            }

            container = provider.get_container(provider_config)
            container.start()

            self.active_containers[provider.name] = container

            updates = provider.update_settings(container, self.settings, provider_config)

            self._merge_updates(all_updates, updates)

        self.settings_updates = all_updates
        return all_updates

    def stop_containers(self) -> None:
        """Stop and remove all active containers."""
        for container in self.active_containers.values():
            try:
                container.stop()
            except Exception:
                ...

        self.active_containers.clear()

    def _merge_updates(self, target: dict[str, Any], updates: dict[str, Any]) -> None:
        """Deep merge settings updates.

        Args:
            target: Target dict to merge into
            updates: Updates to merge
        """
        for key, value in updates.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_updates(target[key], value)
            else:
                target[key] = value

    def _check_unavailable_providers(self) -> None:
        """Check if any unavailable providers would have been auto-detected.

        Raises:
            MissingDependencyError: If a provider is needed but unavailable
        """
        if not UNAVAILABLE_PROVIDERS:
            return

        config = self.get_testcontainers_config()

        for provider_name, (
            extra_name,
            original_error,
        ) in UNAVAILABLE_PROVIDERS.items():
            provider_config = config.get(provider_name, {})

            if provider_config.get("enabled", False):
                self._raise_missing_dependency_error(
                    provider_name,
                    extra_name,
                    original_error,
                    f"TESTCONTAINERS['{provider_name}']",
                )

            if provider_config.get("auto", True) is not False:
                detected_location = self._would_be_auto_detected(provider_name)
                if detected_location:
                    self._raise_missing_dependency_error(
                        provider_name, extra_name, original_error, detected_location
                    )

    def _would_be_auto_detected(self, provider_name: str) -> str | None:
        """Check if a provider would be auto-detected from settings.

        Args:
            provider_name: Name of the provider to check

        Returns:
            String describing where it was detected, or None if not detected
        """
        if provider_name == "mysql":
            databases = getattr(self.settings, "DATABASES", {})
            for db_name, db_config in databases.items():
                if isinstance(db_config, dict):
                    engine = db_config.get("ENGINE", "")
                    if "mysql" in engine.lower() or "mariadb" in engine.lower():
                        return f"DATABASES['{db_name}']['ENGINE']"

        elif provider_name == "redis":
            caches = getattr(self.settings, "CACHES", {})
            for cache_name, cache_config in caches.items():
                if isinstance(cache_config, dict):
                    backend = cache_config.get("BACKEND", "")
                    if "redis" in backend.lower():
                        return f"CACHES['{cache_name}']['BACKEND']"

            celery_broker = getattr(self.settings, "CELERY_BROKER_URL", "")
            if "redis://" in celery_broker.lower():
                return "CELERY_BROKER_URL"

            session_engine = getattr(self.settings, "SESSION_ENGINE", "")
            if "redis" in session_engine.lower():
                return "SESSION_ENGINE"

        return None

    def _raise_missing_dependency_error(
        self,
        provider_name: str,
        extra_name: str,
        original_error: Exception,
        detected_in: str,
    ) -> None:
        """Raise a helpful MissingDependencyError.

        Args:
            provider_name: Name of the provider
            extra_name: Name of the pip extra
            original_error: The original import error
            detected_in: Where the provider was detected
        """
        # Capitalize provider name for display
        display_name = provider_name.upper() if provider_name == "mysql" else provider_name.title()

        raise MissingDependencyError(
            provider_name=display_name,
            extra_name=extra_name,
            detected_in=detected_in,
            original_error=original_error,
        )
