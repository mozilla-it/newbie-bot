#!/usr/bin/env bash
source venv/bin/activate
flask db upgrade
exec gunicorn -b :5000 -w 1 --access-logfile - --error-logfile - app:app