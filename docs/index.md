# Django Testcontainers Plus

<p align="center"><em>A plug-and-play testcontainers integration for Django</em></p>

<p align="center">
  <a href="https://pypi.org/project/django-testcontainers-plus/">
    <img src="https://img.shields.io/pypi/v/django-testcontainers-plus.svg" alt="PyPI version">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://github.com/WoodyWoodster/django-testcontainers-plus/actions">
    <img src="https://github.com/WoodyWoodster/django-testcontainers-plus/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
</p>

---

## Installation

```bash
pip install django-testcontainers-plus
```

See the full [Installation Guide](pages/getting-started/installation.md) for extras and options.

---

**Django Testcontainers Plus** makes integration testing with real services effortless. It automatically detects the databases and services your Django project uses and spins up the right Docker containers - no manual configuration required.

## Why Django Testcontainers Plus?

Testing Django applications often requires real external services like PostgreSQL, Redis, or MySQL. Mocking them is fragile. Running them manually is tedious. **Django Testcontainers Plus** solves this by:

<div class="grid cards" markdown>

- :material-lightning-bolt: **Zero Configuration**

    Automatically detects your database and service needs from Django settings - no extra setup required.

- :material-power-plug: **Plug and Play**

    Install, add one line to settings, and go. No manual container management ever.

- :material-database: **Multi-Database**

    Full support for PostgreSQL, MySQL, and MariaDB. MongoDB and SQL Server coming soon.

- :material-test-tube: **Dual Test Runner Support**

    Works with both Django's built-in test runner and pytest out of the box.

</div>

## Quick Look

Set the Django test runner, configure `DATABASES` as usual (no host or port), and run tests:

```python title="settings.py"
TEST_RUNNER = 'django_testcontainers_plus.runner.TestcontainersRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myapp',
    }
}
```

```bash
python manage.py test
```

For pytest, register the plugin in `conftest.py` instead of setting `TEST_RUNNER`:

```python title="conftest.py"
pytest_plugins = ['django_testcontainers_plus.pytest_plugin']
```

```bash
pytest
```

=== "Django Test Runner"

    ```python title="settings.py"
    TEST_RUNNER = 'django_testcontainers_plus.runner.TestcontainersRunner'

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'myapp',
        }
    }
    ```

    ```bash
    python manage.py test
    ```

=== "pytest"

    ```python title="conftest.py"
    pytest_plugins = ['django_testcontainers_plus.pytest_plugin']
    ```

    ```python title="settings.py"
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'test',
        }
    }
    ```

    ```bash
    pytest
    ```

## Supported Services

| Service | Auto-Detection | Extra Required |
|---|---|---|
| **PostgreSQL** | `DATABASES` engine | None |
| **MySQL / MariaDB** | `DATABASES` engine | `[mysql]` |
| **Redis** | `CACHES`, `CELERY_BROKER_URL`, `SESSION_ENGINE` | `[redis]` |
| MongoDB | Coming soon | - |
| **S3 (RustFS)** | `STORAGES`, `DEFAULT_FILE_STORAGE`, `AWS_STORAGE_BUCKET_NAME` | `[s3]` |
| Elasticsearch | Coming soon | - |

## Next Steps

- [Quick Start](pages/getting-started/quickstart.md) - Get up and running in minutes
- [Configuration](pages/user-guide/configuration.md) - Customize container images, credentials, and more
- LLM-friendly copies: [llms.txt](https://django-testcontainers-plus.readthedocs.io/llms.txt) (index) and [llms-full.txt](https://django-testcontainers-plus.readthedocs.io/llms-full.txt) (full docs)