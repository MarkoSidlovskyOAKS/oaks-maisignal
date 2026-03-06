# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MAiSIGNAL is a pharmaceutical market intelligence alert system by OAKS Consulting s.r.o. It monitors Czech drug regulatory events (SUKL drug unavailability reports) and sends branded transactional email alerts to pharma clients via the Ecomail API. Alerts highlight market opportunities when competitor drugs experience supply disruptions.

## Architecture

- **`send_maisignal_alert.sh`** — Bash script that sends a transactional email via Ecomail's REST API (`POST /api/transactional/send-message`). It JSON-escapes an HTML file and posts it with tracking options enabled.
- **`sukl-alert-email-real-data.html`** — Self-contained HTML email template (inline CSS, no external dependencies except Google Fonts). Uses DM Sans / DM Mono typography. Contains SUKL regulatory data, KPI metrics, prescriber/pharmacy tables, and market opportunity analysis.

## Key Commands

```bash
# Send an alert email (requires valid Ecomail API key)
./send_maisignal_alert.sh
```

## Domain Context

- **SUKL** (Státní ústav pro kontrolu léčiv) — Czech State Institute for Drug Control
- **UZIS eRECEPT** — Czech national e-prescription data source for reimbursement/prescription analytics
- **ATC codes** — Anatomical Therapeutic Chemical classification (e.g., N02BF02 = Pregabalin)
- Alert language is Czech; all UI strings, email content, and field labels are in Czech

## Important Notes

- The Ecomail API key in `send_maisignal_alert.sh` is hardcoded — must be extracted to an environment variable or `.env` file before any git commits
- Email HTML is designed for email clients — avoid modern CSS features (flexbox/grid used but may need fallback tables for Outlook)
- The `from_email` domain is `maisignal.cz`
