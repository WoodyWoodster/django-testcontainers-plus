"""MySQL container provider."""

from typing import Any, Dict

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

    def get_container(self, config: Dict[str, Any]) -> DockerContainer:
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

        # Apply additional environment variables if provided
        env = config.get("environment", {})
        for key, value in env.items():
            container = container.with_env(key, value)

        return container

    def update_settings(
        self, container: DockerContainer, settings: Any, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update DATABASES setting with container connection info."""
        # Get connection details from container
        host = container.get_container_host_ip()
        port = container.get_exposed_port(3306)
        username = config.get("username", "test")
        password = config.get("password", "test")
        dbname = config.get("dbname", "test")

        # Find which database(s) use MySQL/MariaDB
        databases = getattr(settings, "DATABASES", {})
        updates = {}

        for db_name, db_config in databases.items():
            if isinstance(db_config, dict):
                engine = db_config.get("ENGINE", "")
                if "mysql" in engine.lower() or "mariadb" in engine.lower():
                    # Update this database configuration
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

    def get_default_config(self) -> Dict[str, Any]:
        return {
            "image": "mysql:8",
            "username": "test",
            "password": "test",
            "dbname": "test",
        }
