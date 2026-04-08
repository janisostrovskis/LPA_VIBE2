# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml ./
RUN pip install -e .

COPY . .

EXPOSE 8000

# Real uvicorn CMD lands in sub-phase 00f once backend/app/main.py exists.
CMD ["python", "-c", "import sys; sys.stderr.write('LPA backend container: app/main.py not yet implemented (sub-phases 00d/00e/00f). Image build and dependency install verified.\\n'); sys.exit(0)"]
