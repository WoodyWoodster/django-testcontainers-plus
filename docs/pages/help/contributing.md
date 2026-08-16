# Contributing

Contributions are welcome! Here's how to get started.

## Development Setup

This project uses [uv](https://github.com/astral-sh/uv) for package management.

```bash
git clone https://github.com/WoodyWoodster/django-testcontainers-plus
cd django-testcontainers-plus
uv sync --all-extras --dev
```

## Running Tests

```bash
uv run pytest
```

```bash
make coverage
```

## Code Quality

Linting:

```bash
uv run ruff check .
make lint
```

Type checking:

```bash
uv run mypy src/
make typecheck
```

## Adding a New Provider

To add support for a new service (e.g. MongoDB):

1. Create `src/django_testcontainers_plus/providers/mongodb.py`
2. Implement the `ContainerProvider` abstract base class:

```python
from .base import ContainerProvider

class MongoDBProvider(ContainerProvider):
    @property
    def name(self) -> str:
        return "mongodb"

    def can_auto_detect(self, settings) -> bool:
        # Check Django settings for MongoDB references
        ...

    def get_container(self, config):
        # Create and return a configured DockerContainer
        ...

    def update_settings(self, container, settings, config):
        # Return a dict of Django settings updates
        ...

    def get_default_config(self):
        return {"image": "mongo:7"}
```

3. Register your provider in `src/django_testcontainers_plus/providers/__init__.py`
4. Add tests in `tests/test_mongodb_provider.py`
5. Add documentation in `docs/pages/providers/mongodb.md`

## Documentation

Build the docs locally with:

```bash
uv sync --extra docs
uv run mkdocs build
```

The build writes `site/llms.txt`, `site/llms-full.txt`, and Markdown copies of each page for coding agents. Read the Docs serves `llms.txt` and `llms-full.txt` from the project's default version at the documentation domain root.

## Submitting a Pull Request

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/mongodb-provider`
3. Make your changes with tests
4. Ensure all checks pass: `make lint typecheck coverage`
5. Open a Pull Request against `main`

## Project Structure

```
src/django_testcontainers_plus/
├── __init__.py
├── manager.py          # Container lifecycle orchestration
├── runner.py           # Django test runner integration
├── pytest_plugin.py    # pytest fixtures
├── exceptions.py       # Custom exceptions
├── utils.py            # Utilities
└── providers/
    ├── base.py         # Abstract ContainerProvider
    ├── postgres.py
    ├── mysql.py
    └── redis.py
```