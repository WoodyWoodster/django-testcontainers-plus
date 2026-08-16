# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.7] - Latest

### Added
- LLM-friendly documentation: `llms.txt`, `llms-full.txt`, and per-page Markdown copies via mkdocs-llmstxt

### Changed
- README and PyPI description/keywords so coding agents can distinguish this package from pytest-only Testcontainers plugins

## [0.1.6]

### Changed
- Require Django 5.2+ and declare support for Django 5.2, 6.0, and 6.1

### Added
- Mailhog auto-detection and settings updates for Django 6.1 `MAILERS`

## [0.1.5]

### Changed
- Require `testcontainers>=4.15.0` and import Postgres, MySQL, and Redis containers from `testcontainers.community` to silence deprecation warnings

## [0.1.4]

### Added
- S3-compatible object storage provider (RustFS)
- MkDocs Material documentation site

## [0.1.3]

### Added
- Mailhog provider integration for email testing

### Fixed
- Runner connection recreation on container startup

## [0.1.2]

### Added
- Redis provider support (`[redis]` extra)
- Auto-detection from `CELERY_BROKER_URL` and `SESSION_ENGINE`

## [0.1.1]

### Added
- MySQL / MariaDB provider support (`[mysql]` extra)
- Helpful `MissingDependencyError` with installation instructions

## [0.1.0]

### Added
- Initial release
- PostgreSQL provider (zero-config)
- Django test runner integration (`TestcontainersRunner`)
- pytest plugin (`django_testcontainers_plus.pytest_plugin`)
- Auto-detection from `DATABASES` settings
- `TESTCONTAINERS` setting for custom configuration