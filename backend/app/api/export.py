from pathlib import Path
from zipfile import ZipFile

import geopandas as gpd
import matplotlib.pyplot as plt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from shapely.geometry import shape
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.features import _check_project
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Building, Road, WaterBody, Vegetation, Parcel, User

router = APIRouter(prefix="/api/v1/export", tags=["export"])
settings = get_settings()

MODELS = {"buildings": Building, "roads": Road, "water": WaterBody, "vegetation": Vegetation, "parcels": Parcel}


def _filters(confidence=None, roof_type=None, min_area=None, model_version=None):
    return {"confidence": confidence, "roof_type": roof_type, "min_area": min_area, "model_version": model_version}


def _rows(project_id, layer, db, confidence=None, roof_type=None, min_area=None, model_version=None):
    model = MODELS[layer]
    rows = db.query(model).filter(model.project_id == project_id).all()
    output = []
    for row in rows:
        conf = float(getattr(row, "confidence", getattr(row, "boundary_confidence", 0)))
        if confidence is not None and conf < confidence: continue
        if roof_type and getattr(row, "roof_type", None) != roof_type: continue
        if min_area is not None and float(getattr(row, "area_m2", 0) or 0) < min_area: continue
        if model_version and getattr(row, "model_version", None) != model_version: continue
        geometry = row.geometry
        if hasattr(geometry, "__geo_interface__"): geometry = geometry.__geo_interface__
        output.append({"type":"Feature","geometry":geometry,"properties":{"id":row.id,"feature_type":layer.rstrip("s"),"confidence":conf,"model_version":getattr(row,"model_version",None),"area_m2":getattr(row,"area_m2",None),"perimeter_m":getattr(row,"perimeter_m",None),"length_m":getattr(row,"length_m",None),"width_m":getattr(row,"width_m",None),"roof_type":getattr(row,"roof_type",None),"roof_confidence":getattr(row,"roof_confidence",None),"boundary_confidence":getattr(row,"boundary_confidence",None),"coverage_pct":getattr(row,"coverage_pct",None),"compactness":getattr(row,"compactness",None),"source_image_id":getattr(row,"source_image_id",None),"is_authoritative":getattr(row,"is_authoritative",False)}})
    return output


def _shapefile_properties(features):
    mapping = {"feature_type":"feat_type","model_version":"model_ver","area_m2":"area_m2","perimeter_m":"perim_m","compactness":"compact","roof_confidence":"roof_conf","boundary_confidence":"bound_conf","source_image_id":"source_img","coverage_pct":"coverage","is_authoritative":"authoritat"}
    return [{mapping.get(k,k[:10]):v for k,v in f["properties"].items()} for f in features]


@router.get("/geojson")
def geojson_export(project_id: str, layer: str = "buildings", confidence: float | None = None, roof_type: str | None = None, min_area: float | None = None, model_version: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _check_project(db, project_id, user)
    layers = list(MODELS) if layer == "all" else [layer]
    if any(x not in MODELS for x in layers): raise HTTPException(400, "Unknown export layer")
    features = [f for x in layers for f in _rows(project_id, x, db, **_filters(confidence, roof_type, min_area, model_version))]
    if not features: raise HTTPException(404, "No features to export")
    import json
    return {"type":"FeatureCollection","features":features}


@router.get("/csv")
def csv_export(project_id: str, layer: str = "buildings", db: Session = Depends(get_db), user: User = Depends(current_user)):
    _check_project(db, project_id, user)
    if layer not in MODELS: raise HTTPException(400, "Unknown layer")
    rows = _rows(project_id, layer, db)
    if not rows: raise HTTPException(404, "No features to export")
    import csv
    from io import StringIO
    sio=StringIO(); props=rows[0]["properties"]; w=csv.DictWriter(sio,fieldnames=props.keys()); w.writeheader(); [w.writerow(f["properties"]) for f in rows]
    out=settings.storage_root/"exports"/project_id; out.mkdir(parents=True,exist_ok=True)
    p=out/f"{layer}.csv"; p.write_text(sio.getvalue()); return FileResponse(p,media_type="text/csv",filename=p.name)


@router.get("/shapefile")
def shapefile_export(project_id: str, layer: str = "buildings", confidence: float | None = None, roof_type: str | None = None, min_area: float | None = None, model_version: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _check_project(db, project_id, user)
    if layer not in MODELS: raise HTTPException(400, "Shapefile export requires a single layer")
    features = _rows(project_id, layer, db, **_filters(confidence, roof_type, min_area, model_version))
    if not features: raise HTTPException(404, "No features to export")
    gdf = gpd.GeoDataFrame(_shapefile_properties(features), geometry=[shape(f["geometry"]) for f in features], crs="EPSG:4326")
    out_dir = settings.storage_root / "exports" / project_id; out_dir.mkdir(parents=True, exist_ok=True)
    shp = out_dir / f"{layer}.shp"; gdf.to_file(shp, driver="ESRI Shapefile")
    archive = out_dir / f"{layer}.zip"
    with ZipFile(archive, "w") as zf:
        for suffix in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
            component = out_dir / f"{shp.stem}{suffix}"
            if component.exists(): zf.write(component, arcname=component.name)
    return FileResponse(archive, media_type="application/zip", filename=archive.name)


@router.get("/geopackage")
def geopackage_export(project_id: str, layer: str = "all", confidence: float | None = None, roof_type: str | None = None, min_area: float | None = None, model_version: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _check_project(db, project_id, user)
    layers = list(MODELS) if layer == "all" else [layer]
    if any(x not in MODELS for x in layers): raise HTTPException(400, "Unknown export layer")
    out_dir = settings.storage_root / "exports" / project_id; out_dir.mkdir(parents=True, exist_ok=True)
    gpkg = out_dir / "svamitrai_features.gpkg"
    wrote = False
    for name in layers:
        rows = _rows(project_id, name, db, **_filters(confidence, roof_type, min_area, model_version))
        if not rows: continue
        gdf = gpd.GeoDataFrame([f["properties"] for f in rows], geometry=[shape(f["geometry"]) for f in rows], crs="EPSG:4326")
        gdf.to_file(gpkg, layer=name, driver="GPKG", mode="w" if not wrote else "a"); wrote = True
    if not gpkg.exists(): raise HTTPException(404, "No features to export")
    return FileResponse(gpkg, media_type="application/geopackage+sqlite3", filename=gpkg.name)


@router.get("/report")
def report(project_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _check_project(db, project_id, user)
    from app.services.report import generate_report
    path = generate_report(db, project_id)
    return FileResponse(path, media_type="application/pdf", filename=Path(path).name)


@router.get("/png-map")
def png_map(project_id: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _check_project(db, project_id, user)
    features = [f for layer in MODELS for f in _rows(project_id, layer, db)]
    if not features: raise HTTPException(404, "No features available for map export")
    fig, ax = plt.subplots(figsize=(10, 8))
    for f in features:
        gpd.GeoSeries([shape(f["geometry"])], crs="EPSG:4326").plot(ax=ax, alpha=0.45)
    ax.set_title("SVAMITRAI Feature Export"); ax.set_axis_off()
    out_dir=settings.storage_root/"exports"/project_id; out_dir.mkdir(parents=True,exist_ok=True)
    path=out_dir/"feature-map.png"; fig.savefig(path,dpi=160,bbox_inches="tight"); plt.close(fig)
    return FileResponse(path,media_type="image/png",filename=path.name)
