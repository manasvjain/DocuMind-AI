# SVAMITRAI Architecture
React/TypeScript GIS UI → FastAPI REST API/JWT/RBAC → PostgreSQL/PostGIS + object storage + asynchronous job queue → processing worker → raster/GIS + PyTorch segmentation → vectorized features → GeoJSON/CSV/Shapefile/GeoPackage/PDF/PNG.
The model layer exposes U-Net, DeepLabV3+-style and SegFormer-style implementations behind a common factory. Large orthophotos are processed in windows rather than loaded as one array.
