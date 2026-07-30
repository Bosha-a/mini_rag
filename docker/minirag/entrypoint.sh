#!/bin/bash
set -e 

echo "Runnnig database migrations..."

cd /app/models/db_schemes/minirag/
alembic upgrade head
cd /app

exec "$@"