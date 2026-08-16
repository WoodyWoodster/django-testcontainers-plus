# Changelog

All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.5] - Latest

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