#!/usr/bin/env bash
# Script de compilación y migración automática para Railway / Render
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
