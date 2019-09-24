#!/bin/bash
PYTHONPATH="/usr/src/app:$PYTHONPATH"
export PYTHONPATH
FLASK_APP=app.py
flask db revision
flask db upgrade



