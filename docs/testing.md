# Testing
Run `python -m compileall -q backend ml gis scripts` and `pytest -q`. Frontend uses `npm install`, `npm run build`, `npm run lint`. CI runs backend tests, Ruff, frontend build/lint and Trivy.
