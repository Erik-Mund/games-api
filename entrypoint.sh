#!/usr/bin/env sh

echo "Running migrations..."
flask --app GameBaseAPI.run:app db upgrade

echo "Starting gunicorn..."
exec gunicorn GameBaseAPI.run:app --bind 0.0.0.0:$PORT