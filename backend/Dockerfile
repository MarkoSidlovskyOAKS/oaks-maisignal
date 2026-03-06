FROM python:3.14-slim@sha256:6a27522252aef8432841f224d9baaa6e9fce07b07584154fa0b9a96603af7456

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
