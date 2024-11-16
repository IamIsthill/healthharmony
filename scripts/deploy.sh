#!/usr/bin/env bash

set -e

RUN_MANAGE='poetry run python -m healthharmony.manage'

echo 'Running migrations...'
$RUN_MANAGE migrate --no-input
$RUN_MANAGE loaddata data.json

exec poetry run daphne healthharmony.app.asgi:application -p 8000 -b 0.0.0.0
