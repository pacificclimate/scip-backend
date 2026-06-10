FROM python:3.12-slim AS builder

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -yq install \
    build-essential \
    libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install poetry==1.8.5

COPY pyproject.toml poetry.lock README.md ./
COPY scip ./scip

RUN poetry config virtualenvs.in-project true && \
    poetry install --only main


FROM python:3.12-slim

LABEL maintainer="PCIC DevOps <pcic.devops@uvic.ca>"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get -yq install \
    curl \
    libpq5 \
    postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app /app

ENV PATH=/app/.venv/bin:$PATH
ENV FLASK_APP=scip.wsgi:app

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/api/readyz || exit 1

CMD ["gunicorn", "-b", "0.0.0.0:5000", "scip.wsgi:app"]