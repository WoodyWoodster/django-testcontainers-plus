from .base import ContainerProvider
from .postgres import PostgresProvider

__all__ = [
    "ContainerProvider",
    "PostgresProvider",
    "PROVIDER_REGISTRY",
    "UNAVAILABLE_PROVIDERS",
]

PROVIDER_REGISTRY: list[ContainerProvider] = [
    PostgresProvider(),
]

UNAVAILABLE_PROVIDERS: dict[str, tuple[str, Exception]] = {}

try:
    from .mysql import MySQLProvider

    PROVIDER_REGISTRY.append(MySQLProvider())
    __all__.append("MySQLProvider")
except ImportError as e:
    UNAVAILABLE_PROVIDERS["mysql"] = ("mysql", e)

try:
    from .redis import RedisProvider

    PROVIDER_REGISTRY.append(RedisProvider())
    __all__.append("RedisProvider")
except ImportError as e:
    UNAVAILABLE_PROVIDERS["redis"] = ("redis", e)
