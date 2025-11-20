from .exceptions import DjangoTestcontainersError, MissingDependencyError
from .manager import ContainerManager
from .providers import ContainerProvider, PostgresProvider
from .runner import TestcontainersRunner

__version__ = "0.1.1"

__all__ = [
    "ContainerManager",
    "ContainerProvider",
    "PostgresProvider",
    "TestcontainersRunner",
    "DjangoTestcontainersError",
    "MissingDependencyError",
]

# try:
#     from .providers import MySQLProvider
#
#     __all__.append("MySQLProvider")
# except ImportError:
#     pass
#
# try:
#     from .providers import RedisProvider
#
#     __all__.append("RedisProvider")
# except ImportError:
#     pass
