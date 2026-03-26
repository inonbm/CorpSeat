#!/bin/sh
set -e

DB_PATH="${DB_PATH:-/app/corpseat.db}"

echo "Checking database initialization at $DB_PATH..."
if [ ! -f "$DB_PATH" ]; then
    echo "Database not found. Initializing schema securely..."
    python3 -c "from dal.db import init_db; init_db()"
    echo "Database initialized successfully."
else
    echo "Database at $DB_PATH already exists."
fi

echo "Starting Gunicorn server on 0.0.0.0:5000..."
exec gunicorn -w 4 -b 0.0.0.0:5000 app:app
