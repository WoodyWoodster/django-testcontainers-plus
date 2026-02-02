from collections.abc import Generator
from typing import Any

import pytest
from django.conf import settings

from .manager import ContainerManager
from .utils import apply_settings_updates, recreate_database_connections, restore_settings

_container_manager: ContainerManager | None = None
_original_settings: dict[str, Any] = {}
_context: dict[str, Any] = {}


def pytest_configure(config: pytest.Config) -> None:
    """Capture original Django settings before test setup overwrites them.

    Django's setup_test_environment() overwrites certain settings
    (e.g. EMAIL_BACKEND is set to locmem). We capture originals here
    so providers can use them for auto-detection.
    """
    global _context
    try:
        _context = {
            "original_email_backend": getattr(settings, "EMAIL_BACKEND", None),
        }
    except Exception:
        # Settings may not be configured yet
        _context = {}


@pytest.fixture(scope="session")
def django_db_setup(
    request: pytest.FixtureRequest,
    django_test_environment: Any,
    django_db_blocker: Any,
    django_db_use_migrations: bool,
    django_db_keepdb: bool,
    django_db_createdb: bool,
    django_db_modify_db_settings: None,
) -> Generator[None, None, None]:
    """Override pytest-django's django_db_setup to start containers first.

    This fixture:
    1. Starts testcontainers before database setup
    2. Clears Django's connection cache to pick up new settings
    3. Reconfigures database connections with container settings
    4. Sets up the test database using pytest-django's logic
    5. Cleans up containers after all tests complete
    """
    global _container_manager, _original_settings

    # Start containers and get settings updates
    _container_manager = ContainerManager(settings, context=_context)
    settings_updates = _container_manager.start_containers()

    if settings_updates:
        apply_settings_updates(settings_updates, _original_settings)
        recreate_database_connections()

    # Now run pytest-django's database setup logic
    from django.test.utils import setup_databases, teardown_databases

    with django_db_blocker.unblock():
        db_cfg = setup_databases(
            verbosity=request.config.option.verbose,
            interactive=False,
            keepdb=django_db_keepdb,
            debug_sql=getattr(request.config.option, "debug_sql", False),
            parallel=0,
            aliases=None,
            serialized_aliases=None,
            run_migrations=django_db_use_migrations,
        )

    yield

    # Teardown
    with django_db_blocker.unblock():
        try:
            teardown_databases(db_cfg, verbosity=request.config.option.verbose)
        except Exception:
            pass

    if _container_manager is not None:
        restore_settings(_original_settings)
        print("Stopping test containers...")
        _container_manager.stop_containers()
        _container_manager = None


@pytest.fixture(scope="session")
def testcontainers_manager() -> ContainerManager | None:
    """Get the active container manager.

    Returns:
        ContainerManager instance with active containers
    """
    return _container_manager


pytest_plugins = ["django_testcontainers_plus.pytest_plugin"]
