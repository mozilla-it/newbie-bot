#!/bin/bash

ENVDIR="/usr/src/env"
TMPDIR="/usr/src/app"
TMPFILE="$(mktemp -p $TMPDIR)"

# Exit if not in k8s
[ -z "$KUBERNETES_SERVICE_HOST" ] && exit 0

# Exit if ENV is not where we expect
[ ! -d "$ENVDIR" ] && exit 0

cd $ENVDIR

# Convert to the file python decouple expects
for VAR in *; do
    echo $VAR=$(cat $VAR) >> $TMPFILE
done

# Check for updates if there is existing .env
if [ -f "${TMPDIR}/.env" ]; then
    diff $TMPFILE ${TMPDIR}/.env >/dev/null
    [ $? -eq 0 ] && rm $TMPFILE; exit 0
fi

# Put the file in place, finished
mv $TMPFILE ${TMPDIR}/.env
