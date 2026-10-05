# SVAMITRAI Project Analysis

## Objective
Build an AI + GIS platform that accepts drone orthophotos and extracts buildings, roads, water, vegetation and candidate property boundaries; calculates GIS attributes; supports roof classification; visualizes results; and exports analysis.

## Architecture
React/TypeScript GIS UI → FastAPI REST/JWT → database/object storage/job queue → worker → raster validation/tiling → PyTorch segmentation → GIS vectorization → PostGIS/SQLite → GeoJSON/analytics/exports/reports.

## Stack
Frontend: React, TypeScript, Vite, Tailwind, TanStack Query, React Router, Recharts, Leaflet.
Backend: Python, FastAPI, Pydantic, SQLAlchemy, Alembic.
ML: PyTorch, torchvision, OpenCV, NumPy, Pandas, scikit-learn; optional Albumentations, SHAP, LIME.
GIS: Rasterio, GeoPandas, Shapely, PyProj.
Cloud: GCS, Cloud Run, Cloud SQL/PostGIS, Pub/Sub/Redis, Secret Manager, Cloud Logging, Artifact Registry.

## Requirements covered
Authentication/RBAC; project management; orthophoto ingestion; memory-efficient tiling; configurable segmentation models; evaluation; roof classification; GIS polygonization; spatial filtering/queries; live analytics; model registry; explainability adapters; export/report generation; Docker/CI; security controls; tests and documentation.

## Data policy
No random external dataset was downloaded. Demo data is synthetic and generated locally. Production metrics must come from a documented real dataset/test split. Candidate parcel boundaries require authoritative validation before legal use.

## Roadmap
1. Local vertical slice: auth → project → upload → processing → GIS → map → export.
2. Train/evaluate U-Net, then compare DeepLabV3+ and SegFormer.
3. Add real roof-labelled dataset/checkpoint.
4. Configure GCS/Cloud SQL/PubSub/Cloud Run/Vertex AI in production.
