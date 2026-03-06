# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MAiSIGNAL is a pharmaceutical market intelligence alert system by OAKS Consulting s.r.o. It monitors Czech drug regulatory events (SUKL drug unavailability reports) and sends branded transactional email alerts to pharma clients via the Ecomail API. Alerts highlight market opportunities when competitor drugs experience supply disruptions.

## Repository Structure

This is a monorepo with three top-level components:

- **`snowflake/`** — Snowflake SQL init scripts, L0 tables, seed data, and a SnowSQL runner. Linted with SQLFluff (dialect: `snowflake`).
- **`backend/`** — Python application that sends transactional email alerts via Ecomail's REST API (`POST /transactional/send-message`). Refactored into four testable functions (`load_config`, `load_template`, `build_payload`, `send_alert`). Tested with pytest (98% coverage). Dockerized with a pinned base image and non-root user.
- **`terraform/`** — AWS infrastructure provisioning (ECR, IAM) using Terraform with S3 remote state backend.

## Key Commands

```bash
# Backend — install dependencies
cd backend && pip install -r requirements.txt

# Backend — install dev dependencies (pytest, ruff)
cd backend && pip install -r requirements-dev.txt

# Backend — send an alert email (requires valid Ecomail API key)
cd backend && python src/send_maisignal_alert.py

# Backend — run tests with coverage
cd backend && pytest --cov=src --cov-report=term-missing

# Backend — lint
cd backend && ruff check src/

# Backend — build Docker image
cd backend && docker build -t maisignal-backend .

# Snowflake — lint SQL files
cd snowflake && sqlfluff lint .

# Snowflake — run init, L0, or seed scripts via SnowSQL
cd snowflake && ./run.sh init/
cd snowflake && ./run.sh L0/
cd snowflake && ./run.sh seed/

# Terraform — initialize and validate
cd terraform && terraform init && terraform validate
```

## Domain Context

- **SUKL** (Státní ústav pro kontrolu léčiv) — Czech State Institute for Drug Control
- **UZIS eRECEPT** — Czech national e-prescription data source for reimbursement/prescription analytics
- **ATC codes** — Anatomical Therapeutic Chemical classification (e.g., N02BF02 = Pregabalin)
- Alert language is Czech; all UI strings, email content, and field labels are in Czech

## Important Notes

- The Ecomail API key is loaded from `backend/config/.env` via `python-dotenv` — never hardcode it in source files. For Docker, inject via `docker run -e ECOMAIL_API_KEY=...` (`.env` is excluded from the image)
- Snowflake credentials are loaded from `snowflake/config/.env` by `run.sh` — never hardcode them in source files
- Email HTML is designed for email clients — avoid modern CSS features (flexbox/grid used but may need fallback tables for Outlook)
- The `from_email` domain is `maisignal.cz`
- Terraform state is stored in S3 bucket `oaks-terraform-state`
