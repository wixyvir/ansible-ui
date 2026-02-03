#!/bin/bash
set -e

echo 'Waiting for postgres...'
while ! nc -z $DB_HOSTNAME $DB_PORT; do
    sleep 0.1
done
echo 'PostgreSQL started'

echo 'Running migrations...'
django-admin migrate

echo 'Starting service...'
exec gunicorn --bind 0.0.0.0:8000 --workers=4 ansible_ui.wsgi
