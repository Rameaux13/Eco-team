#!/bin/sh

echo "Waiting for PostgreSQL..."

while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 0.5
done

echo "PostgreSQL is up - continuing"

echo "Starting Celery worker..."
exec celery -A config worker --loglevel=info