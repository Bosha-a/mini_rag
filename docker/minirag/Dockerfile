FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .

RUN uv pip install -r requirements.txt --system

# Copy in the source code
COPY src/ .

# Check for dir it exists 
RUN mkdir -p models/db_schemes/minirag
COPY docker/minirag/alembic.ini /app/models/db_schemes/minirag/alembic.ini

COPY docker/minirag/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

# Run the application 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]