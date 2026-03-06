# Backend — MAiSIGNAL Alert System

Python application that sends pharmaceutical market intelligence alerts via the Ecomail transactional email API. Built with hexagonal architecture (ports and adapters).

## Prerequisites

- Python 3.12+
- pip
- Ecomail account with a valid API key
- Snowflake account (for recipient data and notification logging)

## Setup

1. Create a virtual environment:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create the environment file with your credentials:

   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your Ecomail API key and Snowflake credentials
   ```

## Usage

```bash
python -m maisignal
```

The application will:

- Connect to Snowflake and fetch recipients from the per-environment schema (`l0_dev` or `l0_prod`)
- Load the HTML email template from `templates/`
- Send alerts via `POST https://api2.ecomailapp.cz/transactional/send-message`
- Log notification results to Snowflake (`l0.notification_log`)

## Architecture

Hexagonal architecture with clear separation of concerns:

- **Ports** (`ports/`) — Protocol interfaces (`EmailSender`, `RecipientRepository`, `TemplateLoader`, `NotificationLogger`)
- **Adapters** (`adapters/`) — Implementations (Ecomail API, Snowflake, file system)
- **Domain** (`domain/`) — `AlertService` orchestrates the alert workflow, `models.py` defines `Recipient` and `SendResult`
- **Entry point** (`__main__.py`) — Wires adapters to ports and runs the service

## Testing

Install dev dependencies and run the test suite:

```bash
pip install -r requirements-dev.txt
pytest --cov=src --cov-report=term-missing
```

36 tests, 99% coverage. Minimum threshold: 80%.

Lint with Ruff:

```bash
ruff check src/
```

## Docker

Build and run the container:

```bash
docker build -t maisignal-backend .
docker run -e ECOMAIL_API_KEY=your-api-key-here maisignal-backend
```

The Dockerfile uses a pinned `python:3.12-slim` image digest and runs as a non-root user. Credentials are injected via environment variables — `config/.env` is excluded from the image.

## Structure

```
backend/
├── src/maisignal/
│   ├── __main__.py              # Entry point — wires adapters and runs
│   ├── ports/                   # Protocol interfaces
│   ├── adapters/
│   │   ├── ecomail_sender.py    # Ecomail transactional API adapter
│   │   ├── snowflake_repository.py        # Recipient data from Snowflake
│   │   ├── snowflake_notification_logger.py  # Notification audit log
│   │   └── file_template_loader.py        # HTML template loader
│   └── domain/
│       ├── alert_service.py     # Core use case orchestration
│       └── models.py            # Recipient, SendResult
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_alert_service.py    # AlertService unit tests
│   ├── test_adapters.py         # Adapter unit tests
│   └── test_main.py             # Entry point tests
├── templates/
│   └── sukl-alert-email-real-data.html
├── config/
│   └── .env                     # Credentials (not committed)
├── Dockerfile
├── .dockerignore
├── pyproject.toml               # Ruff, pytest, coverage config
├── requirements.txt             # Production dependencies
└── requirements-dev.txt         # Dev dependencies (pytest, ruff)
```
