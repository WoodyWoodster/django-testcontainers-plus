from typing import Any

from testcontainers.core.generic import DockerContainer
from testcontainers.mysql import MySqlContainer

from .base import ContainerProvider


class MySQLProvider(ContainerProvider):
    """Provider for MySQL/MariaDB containers."""

    @property
    def name(self) -> str:
        return "mysql"

    def can_auto_detect(self, settings: Any) -> bool:
        """Detect MySQL/MariaDB database from DATABASES setting."""
        databases = getattr(settings, "DATABASES", {})
        return any(
            "mysql" in db.get("ENGINE", "").lower() or "mariadb" in db.get("ENGINE", "").lower()
            for db in databases.values()
            if isinstance(db, dict)
        )

    def get_container(self, config: dict[str, Any]) -> DockerContainer:
        """Create MySQL container with configuration."""
        image = config.get("image", "mysql:8")
        username = config.get("username", "test")
        password = config.get("password", "test")
        dbname = config.get("dbname", "test")

        container = MySqlContainer(
            image=image,
            username=username,
            password=password,
            dbname=dbname,
        )

        env = config.get("environment", {})
        for key, value in env.items():
            container = container.with_env(key, value)

        return container

    def update_settings(
        self, container: DockerContainer, settings: Any, config: dict[str, Any]
    ) -> dict[str, Any]:
        """Update DATABASES setting with container connection info."""
        host = container.get_container_host_ip()
        port = container.get_exposed_port(3306)
        username = config.get("username", "test")
        password = config.get("password", "test")
        dbname = config.get("dbname", "test")

        databases = getattr(settings, "DATABASES", {})
        updates: dict[str, Any] = {}

        for db_name, db_config in databases.items():
            if isinstance(db_config, dict):
                engine = db_config.get("ENGINE", "")
                if "mysql" in engine.lower() or "mariadb" in engine.lower():
                    if "DATABASES" not in updates:
                        updates["DATABASES"] = {}
                    updates["DATABASES"][db_name] = {
                        **db_config,
                        "HOST": host,
                        "PORT": port,
                        "USER": username,
                        "PASSWORD": password,
                        "NAME": dbname,
                    }

        return updates

    def get_default_config(self) -> dict[str, Any]:
        return {
            "image": "mysql:8",
            "username": "test",
            "password": "test",
            "dbname": "test",
        }
