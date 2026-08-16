# Installation

## Requirements

- Python **3.10+**
- Django **5.2+**
- Docker (running locally or in CI)

## Basic Installation

Install with uv or pip. PostgreSQL support is included by default.

```bash
uv add django-testcontainers-plus
# or
pip install django-testcontainers-plus
```

=== "uv (recommended)"

    ```bash
    uv add django-testcontainers-plus
    ```

=== "pip"

    ```bash
    pip install django-testcontainers-plus
    ```

## Optional Extras

Some providers require additional client libraries. Install them with the appropriate extra, for example `pip install django-testcontainers-plus[mysql]`, `[redis]`, `[s3]`, or `[all]`.

=== "MySQL / MariaDB"

    ```bash
    pip install django-testcontainers-plus[mysql]
    ```

=== "Redis"

    ```bash
    pip install django-testcontainers-plus[redis]
    ```

=== "All providers"

    ```bash
    pip install django-testcontainers-plus[all]
    ```

!!! tip "Why are extras needed?"
    PostgreSQL works without extras because the base `testcontainers` package includes
    PostgreSQL support. MySQL and Redis require their respective Python client libraries
    (`mysql-connector-python` and `redis`).

## Verify Docker is Available

Django Testcontainers Plus requires Docker to be running. Verify with:

```bash
docker ps
```

If Docker isn't running, start it before running your tests.

## CI Environments

Most CI providers (GitHub Actions, GitLab CI, CircleCI) include Docker by default.
Make sure your CI job has Docker available and installs all required extras:

```bash
pip install django-testcontainers-plus[all]
```

See [Troubleshooting](../help/troubleshooting.md) for common CI issues.