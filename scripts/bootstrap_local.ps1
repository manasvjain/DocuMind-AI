$ErrorActionPreference='Stop'
$env:PYTHONPATH="$PWD\backend;$PWD"
python -m alembic -c backend/alembic.ini upgrade head
python scripts/generate_demo_dataset.py
python scripts/seed_demo.py
