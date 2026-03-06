FROM python:3.12-slim@sha256:ccc7089399c8bb65dd1fb3ed6d55efa538a3f5e7fca3f5988ac3b5b87e593bf0

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY templates/ ./templates/

ENV PYTHONPATH=/app/src

RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --no-create-home appuser

USER appuser

ENTRYPOINT ["python", "-m", "maisignal"]
