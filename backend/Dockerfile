FROM python:3.12-slim@sha256:ac212230555ffb7ec17c214fb4cf036ced11b30b5b460994376b0725c7f6c151

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY templates/ ./templates/

RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --no-create-home appuser

USER appuser

ENTRYPOINT ["python", "src/send_maisignal_alert.py"]
