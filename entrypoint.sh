#!/bin/bash
set -e

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@" 