#!/usr/bin/env bash
PYTHONPATH="/usr/src/app:$PYTHONPATH"
export PYTHONPATH
flask db init
flask db stamp heads
flask db migrate -m "admin table"
flask db upgrade
exec gunicorn -b :5000 -w 1 --access-logfile - --error-logfile - app:app
