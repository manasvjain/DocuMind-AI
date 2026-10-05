# SVAMITRAI — AI-Powered SVAMITVA Feature Extraction from Drone Orthophotos

End-to-end AI + GIS platform for processing drone orthophotos, extracting buildings/roads/water/vegetation and candidate parcel boundaries, calculating GIS attributes, and serving results through a secure FastAPI + React application.

> DEMO DATA POLICY: any included/generated demo imagery is synthetic and is not survey evidence. The system does not fabricate ML metrics or roof predictions.

## Run locally (Windows PowerShell)

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
$env:PYTHONPATH="backend;."
python -m alembic -c backend/alembic.ini upgrade head
python scripts/generate_demo_dataset.py
python scripts/seed_demo.py
uvicorn app.main:app --reload --app-dir backend
```

In another terminal:
```powershell
cd frontend
npm install
npm run dev
```

API: http://localhost:8000/docs
Frontend: http://localhost:5173

## Docker

```powershell
Copy-Item .env.example .env
# set POSTGRES_PASSWORD and JWT_SECRET in .env
docker compose up --build
```

## Workflow

Register/login → create village project → upload GeoTIFF/TIFF/JPG/PNG → create processing job → tiled segmentation → GIS polygonization → feature analytics → map/filter → GeoJSON/CSV/SHP/GPKG/PDF/PNG export.

## ML

U-Net is the baseline. DeepLabV3+-style and SegFormer-style adapters are available through the same model factory. Train with `ml/configs/unet_baseline.yaml`. Roof classification remains `Unknown` until a real labelled roof checkpoint is registered.

## GIS/legal limitation

Candidate parcel boundaries are analytical outputs. They must be validated against authoritative cadastral/survey records before legal use.

## Verification

See `IMPLEMENTATION_STATUS.md` for tested paths and environment limitations.
