# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MAiSIGNAL is a pharmaceutical market intelligence alert system by OAKS Consulting s.r.o. It monitors Czech drug regulatory events (SUKL drug unavailability reports) and sends branded transactional email alerts to pharma clients via the Ecomail API. Alerts highlight market opportunities when competitor drugs experience supply disruptions.

## Repository Structure

This is a monorepo with three top-level components:

- **`snowflake/`** — Snowflake SQL init scripts, L0 tables, seed data, and a SnowSQL runner. Linted with SQLFluff (dialect: `snowflake`).
- **`backend/`** — Python application that sends transactional email alerts via Ecomail's REST API (`POST /transactional/send-message`). Uses hexagonal architecture (`src/maisignal/`) with ports (protocols), adapters (Snowflake, file system, Ecomail API), and a domain service (`AlertService`). Entry point: `python -m maisignal`. Tested with pytest (99% coverage). Dockerized with a pinned base image and non-root user.
- **`terraform/`** — AWS infrastructure provisioning (ECR, IAM) using Terraform with S3 remote state backend.

## Key Commands

```bash
# Backend — setup virtualenv and install deps
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt          # production
pip install -r requirements-dev.txt      # dev (pytest, ruff)

# Backend — send an alert email (requires valid Ecomail API key)
cd backend && python -m maisignal

# Backend — run tests with coverage
cd backend && pytest --cov=src --cov-report=term-missing

# Backend — lint
cd backend && ruff check src/

# Backend — build & run Docker image
cd backend && docker build -t maisignal-backend .
docker run -e ECOMAIL_API_KEY=... maisignal-backend

# Snowflake — lint SQL files
cd snowflake && sqlfluff lint .

# Snowflake — run init, L0, or seed scripts via SnowSQL
cd snowflake && ./run.sh init/
cd snowflake && ./run.sh L0/
cd snowflake && ./run.sh seed/

# Terraform — initialize and validate
cd terraform && terraform init && terraform validate

# Pre-commit — install hooks (once per clone)
pre-commit install

# Pre-commit — run all hooks manually
pre-commit run --all-files
```

## Pre-commit Hooks

Configured in `.pre-commit-config.yaml`. Installed via `pre-commit install`.

| Hook | Scope | Purpose |
|------|-------|---------|
| `trailing-whitespace` | All files | Remove trailing whitespace |
| `end-of-file-fixer` | All files | Ensure files end with newline |
| `check-added-large-files` | All files | Prevent large file commits |
| `ruff` | `backend/` | Python linting (config: `backend/pyproject.toml`) |
| `sqlfluff-lint` | `snowflake/` | SQL linting (dialect: snowflake) |
| `detect-secrets` | All files | Prevent secrets from being committed |

## Domain Context

- **SUKL** (Statni ustav pro kontrolu leciv) — Czech State Institute for Drug Control
- **UZIS eRECEPT** — Czech national e-prescription data source for reimbursement/prescription analytics
- **ATC codes** — Anatomical Therapeutic Chemical classification (e.g., N02BF02 = Pregabalin)
- Alert language is Czech; all UI strings, email content, and field labels are in Czech

## Important Notes

- Never hardcode secrets — all credentials are loaded from `.env` files or environment variables
- The Ecomail API key: `backend/config/.env` locally, `docker run -e ECOMAIL_API_KEY=...` in Docker
- Snowflake credentials: `snowflake/config/.env` (loaded by `run.sh`)
- Email HTML is designed for email clients — avoid modern CSS features (flexbox/grid used but may need fallback tables for Outlook)
- The `from_email` domain is `maisignal.cz`
- Terraform state is stored in S3 bucket `oaks-terraform-state`
- Backend uses Python virtualenv at `backend/venv/` (gitignored)
