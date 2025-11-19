# Django Testcontainers Plus

A plug-and-play testcontainers integration for Django

[![PyPI version](https://badge.fury.io/py/django-testcontainers-plus.svg)](https://badge.fury.io/py/django-testcontainers-plus)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why Django Testcontainers Plus?

Testing Django applications often requires external services like PostgreSQL, Redis, or S3. Django Testcontainers Plus makes this effortless by:

- **Zero Configuration**: Automatically detects your database and service needs from Django settings
- **Plug and Play**: Install, add to settings, and go - no manual container management
- **Database Agnostic**: Supports PostgreSQL, MySQL, MariaDB, MongoDB, and more
- **Beyond Databases**: Redis for caching, MinIO for S3, and other services
- **Dual Compatibility**: Works with both Django's test runner and pytest
- **Smart Defaults**: Sensible defaults with full customization when needed

## Installation

```bash
# Using uv (recommended)
uv add django-testcontainers-plus

# Using pip
pip install django-testcontainers-plus
```

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

## Development

This project uses [uv](https://github.com/astral-sh/uv) for package management.

```bash
# Clone the repository
git clone https://github.com/woodywoodster/django-testcontainers-plus
cd django-testcontainers-plus

# Install dependencies
uv sync --dev

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
