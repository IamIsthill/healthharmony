#!/usr/bin/env bash

set -e

RUN_MANAGE='poetry run python -m healthharmony.manage'

echo 'Collecting static files...'
$RUN_MANAGE collectstatic --no-input

echo 'Running migrations...'
$RUN_MANAGE migrate --no-input
