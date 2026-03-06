# Backend — MAiSIGNAL Alert System

Python application that sends pharmaceutical market intelligence alerts via the Ecomail transactional email API.

## Prerequisites

- Python 3.12+
- pip
- Ecomail account with a valid API key

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

3. Create the environment file with your Ecomail API key:

   ```bash
   echo 'ECOMAIL_API_KEY=your-api-key-here' > config/.env
   ```

## Usage

```bash
python src/send_maisignal_alert.py
```

The script will:

- Load the API key from `config/.env` (or from the `ECOMAIL_API_KEY` environment variable)
- Read the HTML email template from `templates/`
- Send the email via `POST https://api2.ecomailapp.cz/transactional/send-message`
- Enable click and open tracking

## Testing

Install dev dependencies and run the test suite:

```bash
pip install -r requirements-dev.txt
pytest --cov=src --cov-report=term-missing
```

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

The Dockerfile uses a pinned `python:3.12-slim` image digest and runs as a non-root user. The API key is injected via environment variable — `config/.env` is excluded from the image.

## Structure

```
backend/
├── src/
│   └── send_maisignal_alert.py   # Alert sender (load_config, load_template, build_payload, send_alert)
├── tests/
│   ├── conftest.py               # Shared fixtures
│   └── test_send_maisignal_alert.py  # 19 test cases (98% coverage)
├── templates/
│   └── sukl-alert-email-real-data.html  # HTML email template
├── config/
│   └── .env                      # API key (not committed)
├── Dockerfile
├── .dockerignore
├── pyproject.toml                # Ruff, pytest, coverage config
├── requirements.txt              # Production dependencies
└── requirements-dev.txt          # Dev dependencies (pytest, ruff)
```
