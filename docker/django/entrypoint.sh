#!/bin/sh
set -e

# 1. Fallback defaults if env vars are missing
DB_PRIMARY_HOST=${DB_PRIMARY_HOST:-primary}
DB_PORT=${DB_PORT:-5432}
DB_USER=${DB_USER:-postgres}

echo "Wait for database at $DB_PRIMARY_HOST:$DB_PORT..."

# 2. Add a counter so it doesn't loop for eternity if something is broken
MAX_RETRIES=10
COUNT=0

until pg_isready -h "$DB_PRIMARY_HOST" -p "$DB_PORT" -U "$DB_USER" || [ $COUNT -eq $MAX_RETRIES ]; do
  echo "Database is unavailable - sleeping (Attempt $COUNT/$MAX_RETRIES)"
  COUNT=$((COUNT + 1))
  sleep 1
done

if [ $COUNT -eq $MAX_RETRIES ]; then
  echo "ERROR: Database connection timed out!"
  exit 1
fi

echo "Database is up - executing migrations"
python manage.py migrate

echo "Collecting static files"
python manage.py collectstatic --noinput --clear

# NEW: Conditional Execution
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "1" ]; then
    echo "Starting Development Server (runserver)"
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Starting Production Server (Gunicorn + Uvicorn)"
    exec gunicorn config.asgi:application \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --access-logfile - \
        --error-logfile -
fi
