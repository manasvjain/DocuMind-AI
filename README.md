# SVAMITRAI — AI-Powered SVAMITVA Feature Extraction from Drone Orthophotos

SVAMITRAI is a modular AI + GIS platform for extracting geospatial features from drone orthophotos. It is designed around the SVAMITVA land-survey use case and supports real semantic-segmentation inference, GIS vectorization, spatial analytics, and cloud-ready deployment.

> **Important:** This repository includes a clearly marked synthetic demo dataset for end-to-end testing. It is not a substitute for an authoritative survey dataset or cadastral record. No production ML performance numbers are fabricated.

## Quick start

### Local Python environment
```bash
cp .env.example .env
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r backend/requirements.txt
export PYTHONPATH=backend   # PowerShell: $env:PYTHONPATH="backend"
python -m alembic -c backend/alembic.ini upgrade head
uvicorn app.main:app --reload --app-dir backend
```

### Seed the explicit synthetic demo
```bash
bash scripts/bootstrap_local.sh
# PowerShell: .\\scripts\\bootstrap_local.ps1
```
The bootstrap script creates a local demo administrator. Set `DEMO_ADMIN_PASSWORD` to choose the password; otherwise it generates a random password and prints it. Demo accounts/data are local-only.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker compose up --build
```

API: http://localhost:8000/docs  
Frontend: http://localhost:5173

## Demo workflow
The project contains a synthetic, georeferenced orthophoto and matching segmentation labels under `data/demo/`. The demo worker can execute the same tiling → model inference → GIS vectorization path while clearly marking outputs as demo assets.

## Training
See `docs/training.md` and `ml/configs/unet_baseline.yaml`. The included trainer supports deterministic seeds, checkpointing, early stopping, LR scheduling, mixed precision when CUDA is available, and evaluation outputs.

## Project structure
- `frontend/` React + TypeScript GIS dashboard
- `backend/` FastAPI application, DB models, API, jobs, ML/GIS services
- `ml/` reusable model/training/evaluation/inference components
- `gis/` raster/vector/export helpers
- `data/demo/` synthetic demo input/labels
- `docs/` architecture, API, DB, ML/GIS, deployment and testing docs
- `.github/workflows/` CI workflows

## Limitations
- Roof labels are not supplied by the workspace. Roof classification therefore returns `Unknown` until a labelled roof dataset/checkpoint is configured.
- Real-world accuracy depends on the training dataset, GSD, sensor characteristics, annotation quality, and geographic generalization.
- AI-generated parcel boundaries are analytical candidates and require validation against authoritative cadastral/survey records before legal use.

## Verification
See `IMPLEMENTATION_STATUS.md` for verified checks and the exact environment limitations.
