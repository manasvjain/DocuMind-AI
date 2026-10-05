#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="${PWD}/backend:${PWD}:${PYTHONPATH:-}"
python -m alembic -c backend/alembic.ini upgrade head
python scripts/generate_demo_dataset.py
python scripts/seed_demo.py
