# Django Testcontainers Plus

A plug-and-play testcontainers integration for Django

[![PyPI version](https://img.shields.io/pypi/v/django-testcontainers-plus.svg)](https://pypi.org/project/django-testcontainers-plus/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why Django Testcontainers Plus?

Testing Django applications often requires external services like PostgreSQL, Redis, or S3. Django Testcontainers Plus makes this effortless by:

- **Zero Configuration**: Automatically detects your database and service needs from Django settings
- **Plug and Play**: Install, add to settings, and go - no manual container management
- **Database Agnostic**: Supports PostgreSQL, MySQL, MariaDB, and more
- **Beyond Databases**: Redis for caching, MinIO for S3, and other services
- **Dual Compatibility**: Works with both Django's test runner and pytest
- **Smart Defaults**: Sensible defaults with full customization when needed

## Installation

### Basic Installation

```bash
# Using uv (recommended)
uv add django-testcontainers-plus

# Using pip
pip install django-testcontainers-plus
```

### Optional Extras for containers

```bash
# MySQL/MariaDB support
pip install django-testcontainers-plus[mysql]

# Redis support
pip install django-testcontainers-plus[redis]

# Or install both
pip install django-testcontainers-plus[all]
```

**Note** Postgres works by default so doesn't need to be installed like the above

## Quick Start

### Option 1: Django Test Runner (Minimal Setup)

```python
# settings.py
TEST_RUNNER = 'django_testcontainers_plus.runner.TestcontainersRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myapp',
    }
}
```

That's it! Run your tests:

```bash
python manage.py test
```

PostgreSQL will automatically start in a container, run your tests, and clean up.

### Option 2: pytest-django

```python
# conftest.py
pytest_plugins = ['django_testcontainers_plus.pytest_plugin']
```

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test',
    }
}
```

Run your tests:

```bash
pytest
```

## Supported Services

### Databases

- PostgreSQL - Auto-detected from `django.db.backends.postgresql`
- MySQL/MariaDB - Auto-detected from `django.db.backends.mysql`
- MongoDB - Coming soon
- SQL Server - Coming soon

### Other Services

- Redis - Auto-detected from cache/Celery settings
- MinIO - S3-compatible storage (coming soon)
- Mailhog - Email testing (coming soon)
- Elasticsearch - Search (coming soon)

## Configuration

### Zero Configuration (Auto-Detection)

Django Testcontainers Plus automatically detects services from your settings:

```python
# PostgreSQL auto-detected
DATABASES = {
    'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': 'test'}
}

# Redis auto-detected
CACHES = {
    'default': {'BACKEND': 'django.core.cache.backends.redis.RedisCache'}
}

# Celery Redis auto-detected
CELERY_BROKER_URL = 'redis://localhost:6379/0'
```

### Custom Configuration

Override defaults when needed:

```python
TESTCONTAINERS = {
    'postgres': {
        'image': 'postgres:16-alpine',
        'username': 'testuser',
        'password': 'testpass',
        'dbname': 'testdb',
    },
    'redis': {
        'image': 'redis:7-alpine',
    },
}
```

### Disable Auto-Detection

```python
TESTCONTAINERS = {
    'postgres': {
        'auto': False,  # Disable auto-detection
        'enabled': True,  # But explicitly enable it
    },
}
```

## Examples

### PostgreSQL with Django Test Runner

```python
# settings.py
TEST_RUNNER = 'django_testcontainers_plus.runner.TestcontainersRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myapp',
    }
}

# Optional: Customize PostgreSQL version
TESTCONTAINERS = {
    'postgres': {
        'image': 'postgres:15',
    }
}
```

```bash
python manage.py test
```

### MySQL with pytest

```python
# conftest.py
pytest_plugins = ['django_testcontainers_plus.pytest_plugin']

# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test',
    }
}
```

```bash
pytest
```

### PostgreSQL + Redis

```python
# settings.py
TEST_RUNNER = 'django_testcontainers_plus.runner.TestcontainersRunner'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
    }
}
```

Both PostgreSQL and Redis containers will start automatically!

## How It Works

1. **Detection**: Scans your Django settings for database engines and service backends
2. **Configuration**: Merges detected needs with any custom `TESTCONTAINERS` config
3. **Startup**: Starts necessary containers before tests run
4. **Injection**: Updates Django settings with container connection details
5. **Cleanup**: Stops and removes containers after tests complete

## Troubleshooting

### Missing Dependency Errors

If you see an error like this:

```
======================================================================
MySQL Support Not Installed
======================================================================

MySQL was detected in your Django settings:
  → DATABASES['default']['ENGINE']

To enable MySQL support, install the required dependencies:
  pip install django-testcontainers-plus[mysql]

Or install all providers:
  pip install django-testcontainers-plus[all]
======================================================================
```

**What happened?** Django Testcontainers Plus detected that you're using MySQL in your settings, but the MySQL client library (`mysql-connector-python`) isn't installed.

**Solution:** Install the extra for your database:

```bash
# For MySQL/MariaDB
pip install django-testcontainers-plus[mysql]

# For Redis
pip install django-testcontainers-plus[redis]

# Or install everything
pip install django-testcontainers-plus[all]
```

### Common Issues

**Q: Why do I need extras for some databases but not Postgres?**

A: PostgreSQL works without extras because the base `testcontainers` package includes PostgreSQL support. MySQL and Redis require their respective Python client libraries.

**Q: Can I disable auto-detection?**

A: Yes! Set `auto: False` in your configuration:

```python
TESTCONTAINERS = {
    'mysql': {
        'auto': False,  # Won't auto-detect MySQL
        'enabled': False,  # Explicitly disable
    }
}
```

**Q: The error message says a service was detected, but I don't use it**

A: Check your settings for Redis/MySQL references in:

- `DATABASES` - Database engines
- `CACHES` - Cache backends
- `CELERY_BROKER_URL` - Celery broker
- `SESSION_ENGINE` - Session storage

You can disable detection for that service with `auto: False`.

**Q: Tests work locally but fail in CI**

A: Make sure your CI environment has:

1. Docker available (most CI providers include it)
2. The correct extras installed: `pip install django-testcontainers-plus[all]`
3. Sufficient permissions to run Docker containers

## Development

This project uses [uv](https://github.com/astral-sh/uv) for package management.

```bash
# Clone the repository
git clone https://github.com/woodywoodster/django-testcontainers-plus
cd django-testcontainers-plus

# Install dependencies (including all optional database clients)
uv sync --all-extras --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Run type checking
uv run mypy src/
```

## Roadmap

- [x] PostgreSQL support
- [x] MySQL/MariaDB support
- [x] Redis support
- [x] Django test runner integration
- [x] pytest plugin
- [ ] MongoDB support
- [ ] MinIO (S3) support
- [ ] Mailhog support
- [ ] Elasticsearch support
- [ ] RabbitMQ support
- [ ] Container reuse between test runs
- [ ] Parallel test support
- [ ] Full documentation site

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

Built with [testcontainers-python](https://github.com/testcontainers/testcontainers-python).
