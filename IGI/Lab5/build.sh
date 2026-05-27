#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
export DEBUG="${DEBUG:-False}"
export SECRET_KEY="${SECRET_KEY:-build-secret}"
python manage.py collectstatic --noinput
