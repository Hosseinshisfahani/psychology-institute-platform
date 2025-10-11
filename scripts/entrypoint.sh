#!/bin/bash

# Django entrypoint script for Docker
set -e

# Function to wait for database
wait_for_db() {
    echo "Waiting for database..."
    while ! python -c "
import psycopg
import os
import sys
try:
    conn = psycopg.connect(
        host=os.environ.get('DATABASE_HOST', 'postgres'),
        port=os.environ.get('DATABASE_PORT', '5432'),
        dbname=os.environ.get('DATABASE_NAME', 'psychology_institute'),
        user=os.environ.get('DATABASE_USER', 'postgres'),
        password=os.environ.get('DATABASE_PASSWORD', 'postgres'),
        connect_timeout=5
    )
    conn.close()
    print('Database is ready!')
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
" 2>/dev/null; do
        echo "Database is unavailable - sleeping"
        sleep 1
    done
}

# Function to wait for Redis
wait_for_redis() {
    echo "Waiting for Redis..."
    while ! python -c "
import redis
import os
try:
    r = redis.Redis(host=os.environ.get('REDIS_HOST', 'redis'), port=6379, db=1)
    r.ping()
    print('Redis is ready!')
except Exception as e:
    print(f'Redis not ready: {e}')
    exit(1)
" 2>/dev/null; do
        echo "Redis is unavailable - sleeping"
        sleep 1
    done
}

# Wait for dependencies
wait_for_db
wait_for_redis

# Run Django management commands
echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating superuser if it doesn't exist..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@mrbone.ir').exists():
    User.objects.create_superuser(
        email='admin@mrbone.ir',
        password='1234',
        first_name='admin',
        last_name='admin'
    )
    print('Superuser created: admin@mrbone.ir / 1234')
else:
    print('Superuser already exists')
EOF

# Execute the main command
echo "Starting Django application..."
exec "$@"
