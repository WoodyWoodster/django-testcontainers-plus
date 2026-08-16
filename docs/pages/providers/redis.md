# Redis Provider

The Redis provider requires the `[redis]` extra to be installed.

## Installation

```bash
pip install django-testcontainers-plus[redis]
```

## Auto-Detection

The provider activates automatically from any of these settings:

| Setting | Detected when |
|---|---|
| `CACHES[*]['BACKEND']` | Contains `redis` |
| `CELERY_BROKER_URL` | Starts with `redis://` |
| `SESSION_ENGINE` | Contains `redis` |

## Minimal Setup

The most common setup is Django's Redis cache backend. Set the test runner (or the pytest plugin) and a `CACHES` backend whose name contains `redis`:

```python title="settings.py"
TEST_RUNNER = 'django_testcontainers_plus.runner.TestcontainersRunner'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
    }
}
```

Celery (`CELERY_BROKER_URL` starting with `redis://`) and Redis sessions (`SESSION_ENGINE`) are also auto-detected.

=== "Django Cache"

    ```python title="settings.py"
    TEST_RUNNER = 'django_testcontainers_plus.runner.TestcontainersRunner'

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://localhost:6379/0',
        }
    }
    ```

=== "Celery Broker"

    ```python title="settings.py"
    TEST_RUNNER = 'django_testcontainers_plus.runner.TestcontainersRunner'

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    ```

=== "Both"

    ```python title="settings.py"
    TEST_RUNNER = 'django_testcontainers_plus.runner.TestcontainersRunner'

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://localhost:6379/0',
        }
    }

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    ```

    A single Redis container serves both the cache and the Celery broker.

## Default Container

| Property | Value |
|---|---|
| Image | `redis:7-alpine` |
| Port | Randomly assigned by Docker |

## Configuration Options

```python title="settings.py"
TESTCONTAINERS = {
    'redis': {
        'image': 'redis:7-alpine',
        'environment': {
            'REDIS_ARGS': '--maxmemory 256mb',
        },
    }
}
```

## Settings Injection

After the Redis container starts, the provider updates your settings automatically:

- `CACHES[*]['LOCATION']` → updated to the container's URL
- `CELERY_BROKER_URL` → updated to the container's URL
- `CELERY_RESULT_BACKEND` → updated to the container's URL

!!! tip "Custom settings updates"
    If you need full control over which settings are updated, you can provide a custom
    `update_settings` dict in your config:

    ```python
    TESTCONTAINERS = {
        'redis': {
            'update_settings': {
                'CACHES': {
                    'default': {
                        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                        'LOCATION': 'redis://localhost:6379/1',  # different DB
                    }
                }
            }
        }
    }
    ```