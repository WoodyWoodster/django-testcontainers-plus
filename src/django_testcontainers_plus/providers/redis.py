"""Redis container provider."""

from typing import Any, Dict

from testcontainers.core.generic import DockerContainer
from testcontainers.redis import RedisContainer

from .base import ContainerProvider


class RedisProvider(ContainerProvider):
    """Provider for Redis containers."""

    @property
    def name(self) -> str:
        return "redis"

    def can_auto_detect(self, settings: Any) -> bool:
        """Detect Redis from CACHES or Celery settings."""
        # Check CACHES setting
        caches = getattr(settings, "CACHES", {})
        has_redis_cache = any(
            "redis" in cache.get("BACKEND", "").lower()
            for cache in caches.values()
            if isinstance(cache, dict)
        )

        # Check Celery broker
        celery_broker = getattr(settings, "CELERY_BROKER_URL", "")
        has_celery_redis = "redis://" in celery_broker.lower()

        # Check session backend
        session_engine = getattr(settings, "SESSION_ENGINE", "")
        has_redis_session = "redis" in session_engine.lower()

        return has_redis_cache or has_celery_redis or has_redis_session

    def get_container(self, config: Dict[str, Any]) -> DockerContainer:
        """Create Redis container with configuration."""
        image = config.get("image", "redis:7-alpine")

        container = RedisContainer(image=image)

        # Apply additional environment variables if provided
        env = config.get("environment", {})
        for key, value in env.items():
            container = container.with_env(key, value)

        return container

    def update_settings(
        self, container: DockerContainer, settings: Any, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update cache/Celery settings with container connection info."""
        host = container.get_container_host_ip()
        port = container.get_exposed_port(6379)
        redis_url = f"redis://{host}:{port}/0"

        updates = {}

        # Check if user provided custom update_settings
        if "update_settings" in config:
            return config["update_settings"]

        # Update CACHES if Redis is detected
        caches = getattr(settings, "CACHES", {})
        for cache_name, cache_config in caches.items():
            if isinstance(cache_config, dict):
                backend = cache_config.get("BACKEND", "")
                if "redis" in backend.lower():
                    if "CACHES" not in updates:
                        updates["CACHES"] = {}
                    updates["CACHES"][cache_name] = {
                        **cache_config,
                        "LOCATION": redis_url,
                    }

        # Update Celery broker if detected
        celery_broker = getattr(settings, "CELERY_BROKER_URL", "")
        if "redis://" in celery_broker.lower():
            updates["CELERY_BROKER_URL"] = redis_url
            updates["CELERY_RESULT_BACKEND"] = redis_url

        return updates

    def get_default_config(self) -> Dict[str, Any]:
        return {
            "image": "redis:7-alpine",
        }
