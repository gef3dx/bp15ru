#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
python3 -c 'import sys; assert sys.version_info >= (3, 12), "Use Python 3.12 or newer"'
if [[ ! -x .venv/bin/python ]]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/setup_local.py
printf '\nOpen http://127.0.0.1:8000 in your browser. Stop with Ctrl+C.\n'
exec .venv/bin/python manage.py runserver 127.0.0.1:8000
