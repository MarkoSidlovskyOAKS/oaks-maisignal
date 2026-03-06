# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.4.0] - 2026-03-06

### Added
- Backend Dockerfile with pinned `python:3.12-slim` digest and non-root user.
- Backend `.dockerignore` to exclude secrets, tests, and caches from image.
- Backend `pyproject.toml` with Ruff, pytest, and coverage configuration.
- Backend `requirements-dev.txt` for dev dependencies (pytest, pytest-cov, ruff).
- Backend test suite with 19 test cases (98% coverage).

### Changed
- Refactored `send_maisignal_alert.py` from monolithic `main()` into four testable functions: `load_config`, `load_template`, `build_payload`, `send_alert`.
- Made `.env` file optional in `load_config` — API key can be injected via environment variable for Docker compatibility.

## [0.3.0] - 2026-03-06

### Added
- Snowflake `maisignal_wh` warehouse (XSMALL, auto-suspend 60s, auto-resume).
- L0 tables: `uzis_erecept`, `client_portfolio`, `client_brands`, `notification_log`.
- Seed data for all L0 tables with real-world LYRICA/PREGLENIX market data.
- SnowSQL runner script (`snowflake/run.sh`) for executing SQL files with `.env` credentials.
- Pre-commit hooks for SQLFluff lint, trailing whitespace, and secret detection.

### Changed
- Renamed Snowflake schema from `raw` to `l0`.
- Renamed `L0_raw/` directory to `L0/`.
- Renumbered init scripts to accommodate new warehouse script (03 → 04).
- Updated service user to use `maisignal_wh` warehouse with warehouse grant.

## [0.2.0] - 2026-03-06

### Added
- Monorepo structure with `snowflake/`, `backend/`, and `terraform/` components.
- Snowflake init scripts: database, schema, and service user creation.
- Snowflake L0 raw table `posledni_platne_hlaseni` for SUKL drug unavailability data.
- SQLFluff configuration for Snowflake dialect.
- Terraform configuration for AWS ECR repository and IAM role (least privilege).
- Component-level README files for snowflake, backend, and terraform.
- CHANGELOG.md.
- LICENSE file (proprietary).

### Changed
- Moved `send_maisignal_alert.py` to `backend/src/`.
- Moved `sukl-alert-email-real-data.html` to `backend/templates/`.
- Moved `requirements.txt` to `backend/`.
- Updated file paths in `send_maisignal_alert.py` for new directory layout.
- Updated root README.md as monorepo overview.
- Updated CLAUDE.md with full architecture description.
- Updated `.gitignore` for all three components.

## [0.1.0] - 2026-03-06

### Added
- Initial MAiSIGNAL alert system.
- Python script to send transactional email via Ecomail API.
- HTML email template with SUKL regulatory data, KPI metrics, and prescriber/pharmacy tables.
