from .base import ContainerProvider
from .mysql import MySQLProvider
from .postgres import PostgresProvider
from .redis import RedisProvider

__all__ = [
    "ContainerProvider",
    "PostgresProvider",
    "MySQLProvider",
    "RedisProvider",
    "PROVIDER_REGISTRY",
]

# Registry of all available providers
PROVIDER_REGISTRY = [
    PostgresProvider(),
    MySQLProvider(),
    RedisProvider(),
]
