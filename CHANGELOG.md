# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.5.0] - 2026-02-09

### Added

- Runtime frontend configuration via `config.js` generated at container startup from `BACKEND_URI` environment variable
- Web container entrypoint script (`docker/entrypoint.web.sh`) for runtime config generation
- No-cache nginx headers for `/config.js` to ensure fresh configuration

### Changed

- Renamed Django module from `ansible_ui` to `ansibeau` across the entire codebase
- Updated GHCR image paths to `ghcr.io/wixyvir/ansibeau/`
- Host status color changed from blue to yellow for changed plays
- Replaced library-based task extraction with custom `_extract_tasks_from_content()` parser that handles serial execution and duplicate task names
- Custom parser merges results across serial batches using `(play_name, task_name, order)` as composite key
- Added `_strip_timestamps()` preprocessing for timestamped log formats before task extraction

### Fixed

- Failed task extraction for serial execution where repeated PLAY headers caused the library to reset play data per batch
- Duplicate task names within a batch being overwritten by the `ansible-output-parser` library
- CI cache key using `poetry.lock` (untracked) instead of `pyproject.toml`, causing stale venv cache hits

## [0.4.0] - 2026-02-03

### Added

- Multi-stage Dockerfile with separate build stages (frontend-builder, backend-builder, api, web)
- Docker Compose configuration with three-service architecture (api, db, web)
- PostgreSQL 15 production database support with `psycopg2`
- gunicorn WSGI HTTP server for Django
- nginx reverse proxy serving frontend SPA and proxying API/admin requests
- `python-decouple` for environment variable configuration (`DJANGO_SECRET`, `DJANGO_PROD`, `DJANGO_ALLOWED_HOSTS`, `DB_*`, etc.)
- `UUIDAutoField` custom field for consistent UUID primary keys across all models
- GitHub Actions CI/CD workflow for automated Docker image builds
- GitHub Container Registry (GHCR) image publishing
- Branch-based Docker image tagging strategy (latest for main, branch name, SHA)
- GitHub Actions build cache for faster Docker builds
- Configurable `CSRF_TRUSTED_ORIGINS` with http/https defaults from `DJANGO_ALLOWED_HOSTS`
- `SECURE_PROXY_SSL_HEADER` and `X-Forwarded-Proto` for reverse proxy HTTPS support
- Production environment template (`.env.production`)
- `.env.example` for backend development configuration
- Rocky Linux 9 as base container image for backend (Python 3.11)
- nginx `client_max_body_size` set to 50M for large log uploads

### Changed

- Squashed database migrations into single initial migration
- Switched default port from 80 to 8000
