FROM python:3.12-slim

RUN useradd --create-home appuser
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

COPY . .
RUN uv sync --frozen --no-dev

RUN chown -R appuser:appuser /app
USER appuser

CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
