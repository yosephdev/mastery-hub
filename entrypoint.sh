#!/bin/bash
# ============================================================
# MasteryHub — Container entrypoint
# Runs on every container start inside Coolify
# ============================================================
set -e

echo "=========================================="
echo "  MasteryHub — starting up"
echo "=========================================="

# Run database migrations (idempotent — safe to run on every start)
echo "[1/3] Applying database migrations..."
python manage.py migrate --noinput

# Push static files to S3 (or collect locally if USE_AWS is not set)
echo "[2/3] Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start Gunicorn
echo "[3/3] Starting Gunicorn..."
echo "      Workers : ${GUNICORN_WORKERS:-2}"
echo "      Port    : ${PORT:-8000}"

exec gunicorn skill_sharing_platform.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-2}" \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
